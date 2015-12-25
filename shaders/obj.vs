
attribute vec3 a_position;
attribute vec3 a_normal;

// uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;

varying vec3 v_position;
varying vec3 v_normal;

void main(void) {
    gl_Position = u_projection * u_view * vec4(a_position, 1.0);
    v_position = a_position;
    v_normal = a_normal;
}