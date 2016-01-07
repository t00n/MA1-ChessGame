#version 130

uniform float u_width;
uniform float u_height;
uniform sampler2D u_texture;
uniform float u_pixel_offset[5] = float[](0.0,1.0,2.0,3.0,4.0);
uniform float u_weights[5];

void main(void) {
    vec2 tex_coord = vec2(gl_FragCoord.x/u_width, gl_FragCoord.y/u_height);
    float dy = 1.0 / u_height;
    vec4 sum = texture(u_texture, tex_coord) * u_weights[0];
    for( int i = 1; i < 5; i++ )
    {
        sum += texture( u_texture, tex_coord + vec2(0.0, u_pixel_offset[i]) * dy ) * u_weights[i];
        sum += texture( u_texture, tex_coord - vec2(0.0, u_pixel_offset[i]) * dy ) * u_weights[i];
    }
    gl_FragColor = sum;
}