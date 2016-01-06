#version 130

uniform sampler2D u_texture;

void main(void) {
    gl_FragColor = texture(u_texture, vec2(gl_FragCoord.x/800, gl_FragCoord.y/600));
}