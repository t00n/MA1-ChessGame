#version 130

varying vec3 v_position;
varying vec3 v_normal;
uniform vec4 u_diffuse;
uniform vec4 u_ambient;
uniform vec4 u_specular;
uniform float u_shininess;

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform vec3 u_light_position;
uniform vec3 u_camera_position;

void main(void) {
    // TODO change to uniform variable
    vec4 u_light_intensities = vec4(1.0,1.0,1.0,1.0);

    // Calcule normal and position in world coordinates
    mat3 normalMatrix = transpose(inverse(mat3(u_model)));
    vec3 normal = normalize(normalMatrix * v_normal);
    vec3 position = vec3(u_model * vec4(v_position, 1));

    // Diffuse component
    vec3 frag_to_light = normalize(u_light_position - position);
    float diffuse_coef = dot(normal, frag_to_light);
    diffuse_coef = clamp(diffuse_coef, 0, 1);
    vec4 diffuse = diffuse_coef * u_diffuse * u_light_intensities;

    // Specular component
    vec3 incidence_vector = -frag_to_light;
    vec3 frag_to_camera = normalize(u_camera_position - position);
    vec3 reflection_vector = reflect(incidence_vector, normal);
    float reflection_angle = dot(frag_to_camera, reflection_vector);
    float specular_exponent = pow(reflection_angle, u_shininess);
    vec4 specular = specular_exponent * u_specular * u_light_intensities;

    // Ambient component
    vec4 ambient = 0.05 * u_ambient * u_light_intensities;

    gl_FragColor = ambient + diffuse;
}