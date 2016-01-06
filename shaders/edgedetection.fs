#version 130

uniform int width;
uniform int height;
uniform sampler2D render_texture;
uniform float threshold;

float luminance(vec3 color) {
    return 0.2126 * color.r + 0.7152 * color.g + 0.0722 * color.b;
}

void main(void) {
    float dx = 1.0/width;
    float dy = 1.0/height;
    float s00 = luminance(texture(render_texture, gl_FragCoord.xy + vec2(-dx, dy)).rgb);
    float s10 = luminance(texture(render_texture, gl_FragCoord.xy + vec2(-dx, 0.0)).rgb);
    float s20 = luminance(texture(render_texture, gl_FragCoord.xy + vec2(-dx,-dy)).rgb);
    float s01 = luminance(texture(render_texture, gl_FragCoord.xy + vec2(0.0, dy)).rgb);
    float s21 = luminance(texture(render_texture, gl_FragCoord.xy + vec2(0.0, -dy)).rgb);
    float s02 = luminance(texture(render_texture, gl_FragCoord.xy + vec2(dx, dy)).rgb);
    float s12 = luminance(texture(render_texture, gl_FragCoord.xy + vec2(dx, 0.0)).rgb);
    float s22 = luminance(texture(render_texture, gl_FragCoord.xy + vec2(dx, -dy)).rgb);
    float sx = s00 + 2 * s10 + s20 - (s02 + 2 * s12 + s22);
    float sy = s00 + 2 * s01 + s02 - (s20 + 2 * s21 + s22);
    float dist = pow(sx, 2) + pow(sy,2);
    if (dist > threshold) {
        gl_FragColor = vec4(1,1,1,1);
    }
    else {
        gl_FragColor = vec4(0,0,0,1);
    }
}