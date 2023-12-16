#version 150

in vec4 vertexColor;

uniform vec4 ColorModulator;

out vec4 fragColor;

void main()
{
    vec4 color = vertexColor;

    if (color.a == 0.0)
    {
        discard;
    }

    // Slot hover background color
    if (color.r == 255/255.0 && color.g == 255/255.0 && color.b == 255/255.0 && color.a == 128/255.0)
    {
        color = vec4(1, 0, 0, 0.2);
    }

    fragColor = color * ColorModulator;
}
