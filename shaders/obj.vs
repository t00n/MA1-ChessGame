
attribute vec3 a_vertex;
// uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;

void main(void) {
    gl_Position = u_projection * u_view * vec4(a_vertex, 1.0);
}