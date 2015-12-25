
varying vec3 v_position;
varying vec3 v_normal;

uniform mat4 u_view;
uniform mat4 u_projection;

void main(void) {
    // Calculate normal in world coordinates
    vec3 normal = normalize(vec4(v_normal,1.0)).xyz;

    // Calculate the location of this fragment (pixel) in world coordinates
    vec3 position = vec3(vec4(v_position, 1));

    // Calculate the vector from this pixels surface to the light source
    vec3 surfaceToLight = vec3(0,10,0) - position;

    // Calculate the cosine of the angle of incidence (brightness)
    float brightness = dot(normal, surfaceToLight) /
                      (length(surfaceToLight) * length(normal));

    brightness = max(min(brightness,1.0),0.0);

    gl_FragColor = brightness * vec4(1.0,1.0,1.0,1.0);
}