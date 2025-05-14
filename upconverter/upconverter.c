#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <sndfile.h>

#define SINK_SAMPLE_RATE 25000000  // 25 MHz output
#define SOURCE_SAMPLE_RATE 48000   // 48 kHz input
#define PWL_FACTOR (SINK_SAMPLE_RATE / SOURCE_SAMPLE_RATE)  // Should be 520

typedef struct {
    float integrator;
    float error;
} delta_sigma_t;

// Linear interpolation upsampling
float *pwl_interpolation(const int16_t *input, int input_len) {
    float *output = (float *)malloc(input_len * PWL_FACTOR * sizeof(float));
    
    for (int i = 0; i < input_len - 1; i++) {
        for (int j = 0; j < PWL_FACTOR; j++) {
            float t = (float)j / PWL_FACTOR;
            output[i * PWL_FACTOR + j] = (1.0f - t) * input[i] + t * input[i + 1];
        }
    }
    return output;
}

// Noise-shaped 4-bit encoding
void delta_sigma_modulate(const float *input, int length, uint8_t *output) {
    delta_sigma_t state = {0};

    for (int i = 0; i < length; i++) {
        float scaled = input[i] / 32768.0f * 7.5f;  // Scale to ±7.5
        float value = scaled + state.error;

        int quantized = (int)(value + 8) & 0x0F;  // Map to 4-bit unsigned range (0–15)
        state.error = value - (quantized - 8);    // Compute new error

        output[i] = (uint8_t)quantized;
    }
}

// Main function
int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s input.wav\n", argv[0]);
        return 1;
    }

    // Open WAV file
    SNDFILE *infile;
    SF_INFO sfinfo;
    infile = sf_open(argv[1], SFM_READ, &sfinfo);
    if (!infile) {
        fprintf(stderr, "Error opening WAV file\n");
        return 1;
    }

    if (sfinfo.samplerate != SOURCE_SAMPLE_RATE || sfinfo.channels != 1 || sfinfo.format != (SF_FORMAT_WAV | SF_FORMAT_PCM_16)) {
        fprintf(stderr, "Unsupported WAV format. Needs 16-bit mono 48kHz.\n");
        sf_close(infile);
        return 1;
    }

    // Read audio data
    int16_t *input_data = (int16_t *)malloc(sfinfo.frames * sizeof(int16_t));
    sf_read_short(infile, input_data, sfinfo.frames);
    sf_close(infile);

    // Processing chain
    float *upsampled = pwl_interpolation(input_data, sfinfo.frames);
    int upsampled_len = sfinfo.frames * PWL_FACTOR;

    uint8_t *output_data = (uint8_t *)malloc(upsampled_len * sizeof(uint8_t));
    delta_sigma_modulate(upsampled, upsampled_len, output_data);

    // Write packed nibbles to stdout
    for (int i = 0; i < upsampled_len; i += 2) {
        uint8_t byte = (output_data[i] << 4) | (output_data[i + 1] & 0x0F);
        putchar(byte);
    }

    // Cleanup
    free(input_data);
    free(upsampled);
    free(output_data);
    return 0;
}
