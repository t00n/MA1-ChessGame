#version 130

uniform float u_width;
uniform float u_height;
uniform sampler2D u_texture;
uniform float u_threshold;

float luma(vec3 color) {
    return 0.2126 * color.r + 0.7152 * color.g + 0.0722 * color.b;
}

void main(void) {
    vec2 tex_coord = vec2(gl_FragCoord.x/u_width, gl_FragCoord.y/u_height);
    vec4 val = texture(u_texture, tex_coord);
    gl_FragColor = val * clamp(luma(val.rgb) - u_threshold, 0.0, 1.0 ) * (1.0 / (1.0 - u_threshold) );
}