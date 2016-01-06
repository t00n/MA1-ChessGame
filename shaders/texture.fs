#version 130

uniform sampler2D u_texture;

void main(void) {
    gl_FragColor = texture(u_texture, gl_FragCoord.xy);
}