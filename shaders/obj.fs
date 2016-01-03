#version 130

varying vec3 v_position;
varying vec3 v_normal;
uniform vec4 u_diffuse;
uniform vec4 u_ambient;

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform vec3 u_light_position;

void main(void) {
    // TODO change to uniform variable
    vec4 u_light_intensities = vec4(1.0,1.0,1.0,1.0);

    mat3 normalMatrix = transpose(inverse(mat3(u_model)));

    // Calculate normal in world coordinates
    vec3 normal = normalize(normalMatrix * v_normal);

    // Calculate the location of this fragment (pixel) in world coordinates
    vec3 position = vec3(u_model * vec4(v_position, 1));

    // Calculate the vector from this pixels surface to the light source
    vec3 surfaceToLight = normalize(u_light_position - position);

    // Calculate the cosine of the angle of incidence
    float diffuse_coef = dot(normal, surfaceToLight);

    diffuse_coef = clamp(diffuse_coef, 0, 1);

    vec4 ambient = 0.05 * u_ambient * u_light_intensities;
    vec4 diffuse = diffuse_coef * u_diffuse * u_light_intensities;

    gl_FragColor = ambient + diffuse;
}