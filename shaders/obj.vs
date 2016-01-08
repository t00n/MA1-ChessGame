
attribute vec3 a_position;
attribute vec3 a_normal;
attribute vec3 a_tangent;
attribute vec3 a_bitangent;

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;

varying vec3 v_position;
varying vec3 v_normal;
varying vec3 v_tangent;
varying vec3 v_bitangent;

void main(void) {
    gl_Position = u_projection * u_view * u_model * vec4(a_position, 1.0);
    v_position = a_position;
    v_normal = a_normal;
    v_tangent = a_tangent;
    v_bitangent = a_bitangent;
}