#version 130

uniform sampler2D u_texture;
uniform float u_width;
uniform float u_height;

void main(void) {
    gl_FragColor = texture(u_texture, vec2(gl_FragCoord.x/u_width, gl_FragCoord.y/u_height));
}