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
    // rgba(1, 1, 1, 128)
    if (color == vec4(1, 1, 1, 0.5019607843137255))
    {
        color = vec4(1, 0, 0, color.a);
    }

    fragColor = color * ColorModulator;
}
