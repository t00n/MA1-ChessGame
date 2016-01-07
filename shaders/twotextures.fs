#version 130

uniform sampler2D u_texture;
uniform sampler2D u_texture2;
uniform float u_width;
uniform float u_height;

void main(void) {
    vec2 tex_coord = vec2(gl_FragCoord.x/u_width, gl_FragCoord.y/u_height);
    gl_FragColor = texture(u_texture, tex_coord) + texture(u_texture2, tex_coord);
}