import math

def draw_circle(rad, res):
    verts = []

    i = 0
    while i <= math.pi*2:
        deg = i * math.pi / 180
        verts.append((rad * math.cos(i), rad * math.sin(i)))

        i += math.pi * 2 / res

    return verts

if __name__ == '__main__':
    for vert in draw_circle(30, 8):
        print(vert)