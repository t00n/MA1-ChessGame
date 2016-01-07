#version 130

uniform float u_width;
uniform float u_height;
uniform sampler2D u_render_texture;
uniform float u_threshold;

float luminance(vec3 color) {
    return 0.2126 * color.r + 0.7152 * color.g + 0.0722 * color.b;
}

void main(void) {
    float x = gl_FragCoord.x/u_width;
    float y = gl_FragCoord.y/u_height;
    float dx = 1.0/u_width;
    float dy = 1.0/u_height;
    float s00 = luminance(texture(u_render_texture, vec2(x - dx, y + dy)).rgb);
    float s10 = luminance(texture(u_render_texture, vec2(x - dx, y)).rgb);
    float s20 = luminance(texture(u_render_texture, vec2(x - dx, y - dy)).rgb);
    float s01 = luminance(texture(u_render_texture, vec2(x, y + dy)).rgb);
    float s21 = luminance(texture(u_render_texture, vec2(x, y - dy)).rgb);
    float s02 = luminance(texture(u_render_texture, vec2(x + dx, y + dy)).rgb);
    float s12 = luminance(texture(u_render_texture, vec2(x + dx, y)).rgb);
    float s22 = luminance(texture(u_render_texture, vec2(x + dx, y - dy)).rgb);
    float sx = s00 + 2 * s10 + s20 - (s02 + 2 * s12 + s22);
    float sy = s00 + 2 * s01 + s02 - (s20 + 2 * s21 + s22);
    float dist = pow(sx, 2) + pow(sy,2);
    if (dist > u_threshold) {
        gl_FragColor = vec4(1,1,1,1);
    }
    else {
        gl_FragColor = vec4(0,0,0,1);
    }
}