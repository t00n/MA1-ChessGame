#version 130

varying vec3 v_position;
varying vec3 v_normal;

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform vec3 u_light_position;

void main(void) {
    mat3 normalMatrix = transpose(inverse(mat3(u_model)));
    // Calculate normal in world coordinates
    vec3 normal = normalize(normalMatrix * v_normal);

    // Calculate the location of this fragment (pixel) in world coordinates
    vec3 position = vec3(u_model * vec4(v_position, 1));

    // Calculate the vector from this pixels surface to the light source
    vec3 surfaceToLight = u_light_position - position;

    // Calculate the cosine of the angle of incidence (brightness)
    float brightness = dot(normal, surfaceToLight) /
                      (length(surfaceToLight) * length(normal));

    brightness = clamp(brightness, 0, 1);

    gl_FragColor = brightness * vec4(1.0,1.0,1.0,1.0);
}