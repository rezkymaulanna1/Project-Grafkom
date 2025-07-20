from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import math

window_width, window_height = 800, 600
draw_mode = "POINT"
mouse_clicks = []
objects = []
colors = {'r': (1, 0, 0), 'g': (0, 1, 0), 'b': (0, 0, 1)}
current_color = colors['r']
line_thickness = 2
temp_drag_start = (0, 0)


clip_window = []
window_active = False

selected_index = -1
transform_mode = None

is_dragging = False
temp_coords = []

INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8

def compute_code(x, y, xmin, ymin, xmax, ymax):
    code = INSIDE
    if x < xmin: code |= LEFT
    elif x > xmax: code |= RIGHT
    if y < ymin: code |= BOTTOM
    elif y > ymax: code |= TOP
    return code

def cohen_sutherland_clip(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    code1 = compute_code(x1, y1, xmin, ymin, xmax, ymax)
    code2 = compute_code(x2, y2, xmin, ymin, xmax, ymax)
    accept = False

    while True:
        if not (code1 | code2):
            accept = True
            break
        elif code1 & code2:
            break
        else:
            x, y = 0, 0
            out_code = code1 if code1 else code2
            if out_code & TOP:
                x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
                y = ymax
            elif out_code & BOTTOM:
                x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
                y = ymin
            elif out_code & RIGHT:
                y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
                x = xmax
            elif out_code & LEFT:
                y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
                x = xmin

            if out_code == code1:
                x1, y1 = x, y
                code1 = compute_code(x1, y1, xmin, ymin, xmax, ymax)
            else:
                x2, y2 = x, y
                code2 = compute_code(x2, y2, xmin, ymin, xmax, ymax)

    if accept:
        return (x1, y1, x2, y2)
    else:
        return None

def shape_inside_window(p1, p2):
    if not window_active: return False
    x1, y1 = clip_window[0]
    x2, y2 = clip_window[1]
    xmin, xmax = min(x1, x2), max(x1, x2)
    ymin, ymax = min(y1, y2), max(y1, y2)
    x_min, y_min = min(p1[0], p2[0]), min(p1[1], p2[1])
    x_max, y_max = max(p1[0], p2[0]), max(p1[1], p2[1])
    return (x_min >= xmin and x_max <= xmax and y_min >= ymin and y_max <= ymax)

def init():
    glClearColor(1, 1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    gluOrtho2D(0, window_width, 0, window_height)

def draw_rect(x1, y1, x2, y2):
    glLineWidth(line_thickness)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x1, y1)
    glVertex2f(x2, y1)
    glVertex2f(x2, y2)
    glVertex2f(x1, y2)
    glEnd()

def draw_ellipse(xc, yc, rx, ry):
    if rx < 1 or ry < 1: return
    glLineWidth(line_thickness)
    glBegin(GL_LINE_LOOP)
    for i in range(0, 360, 2):
        theta = math.radians(i)
        x = xc + rx * math.cos(theta)
        y = yc + ry * math.sin(theta)
        glVertex2f(x, y)
    glEnd()

def inside_window(x, y):
    if not window_active: return False
    x1, y1 = clip_window[0]
    x2, y2 = clip_window[1]
    xmin, xmax = min(x1, x2), max(x1, x2)
    ymin, ymax = min(y1, y2), max(y1, y2)
    return xmin <= x <= xmax and ymin <= y <= ymax

def apply_transformation(obj):
    if transform_mode == 't':  # translate
        dx, dy = 20, 20
        obj['coords'] = [(x + dx, y + dy) for x, y in obj['coords']]
    elif transform_mode == 'o':  # rotate
        if len(obj['coords']) < 2: return
        cx, cy = obj['coords'][0]
        angle = math.radians(15)
        new_coords = []
        for x, y in obj['coords']:
            nx = cx + (x - cx) * math.cos(angle) - (y - cy) * math.sin(angle)
            ny = cy + (x - cx) * math.sin(angle) + (y - cy) * math.cos(angle)
            new_coords.append((nx, ny))
        obj['coords'] = new_coords
    elif transform_mode == 's':  # scale
        if len(obj['coords']) < 2: return
        cx, cy = obj['coords'][0]
        factor = 1.2
        obj['coords'] = [(cx + (x - cx) * factor, cy + (y - cy) * factor) for x, y in obj['coords']]

def display():
    glClear(GL_COLOR_BUFFER_BIT)

    if window_active:
        glColor3f(0, 0, 0)
        draw_rect(*clip_window[0], *clip_window[1])

    for i, obj in enumerate(objects):
        coords = obj['coords']
        color = obj['color']
        type_ = obj['type']

        if i == selected_index and len(coords) == 2:
            glColor3f(1.0, 0.5, 0.0)  # orange highlight
            draw_rect(*coords[0], *coords[1])

        if window_active:
            x1, y1 = clip_window[0]
            x2, y2 = clip_window[1]
            xmin, xmax = min(x1, x2), max(x1, x2)
            ymin, ymax = min(y1, y2), max(y1, y2)

            if type_ == "POINT":
                if inside_window(*coords[0]):
                    glColor3f(0, 1, 0)
                else:
                    glColor3fv(color)
                glPointSize(5)
                glBegin(GL_POINTS)
                glVertex2f(*coords[0])
                glEnd()
                continue

            elif type_ == "LINE":
                # Draw full line with original color
                glColor3fv(color)
                glLineWidth(line_thickness)
                glBegin(GL_LINES)
                glVertex2f(*coords[0])
                glVertex2f(*coords[1])
                glEnd()

                # Draw clipped portion in green
                clipped = cohen_sutherland_clip(*coords[0], *coords[1], xmin, ymin, xmax, ymax)
                if clipped:
                    glColor3f(0, 1, 0)
                    glLineWidth(line_thickness)
                    glBegin(GL_LINES)
                    glVertex2f(clipped[0], clipped[1])
                    glVertex2f(clipped[2], clipped[3])
                    glEnd()
                continue

            elif type_ == "RECT":
                glColor3fv(color)
                draw_rect(*coords[0], *coords[1])

                (x1r, y1r), (x2r, y2r) = coords
                rect_edges = [
                    ((x1r, y1r), (x2r, y1r)),
                    ((x2r, y1r), (x2r, y2r)),
                    ((x2r, y2r), (x1r, y2r)),
                    ((x1r, y2r), (x1r, y1r))
                ]
                for (p1, p2) in rect_edges:
                    clipped = cohen_sutherland_clip(*p1, *p2, xmin, ymin, xmax, ymax)
                    if clipped:
                        glColor3f(0, 1, 0)
                        glLineWidth(line_thickness)
                        glBegin(GL_LINES)
                        glVertex2f(clipped[0], clipped[1])
                        glVertex2f(clipped[2], clipped[3])
                        glEnd()
                continue

            elif type_ == "ELLIPSE":
                glColor3fv(color)
                x1e, y1e = coords[0]
                x2e, y2e = coords[1]
                xc = (x1e + x2e) / 2
                yc = (y1e + y2e) / 2
                rx = abs(x2e - x1e) / 2
                ry = abs(y2e - y1e) / 2

                glLineWidth(line_thickness)
                glBegin(GL_LINE_LOOP)
                for i in range(0, 360, 2):
                    theta = math.radians(i)
                    x = xc + rx * math.cos(theta)
                    y = yc + ry * math.sin(theta)
                    glVertex2f(x, y)
                glEnd()

                glColor3f(0, 1, 0)
                glLineWidth(line_thickness)
                glBegin(GL_POINTS)
                for i in range(0, 360, 2):
                    theta = math.radians(i)
                    x = xc + rx * math.cos(theta)
                    y = yc + ry * math.sin(theta)
                    if inside_window(x, y):
                        glVertex2f(x, y)
                glEnd()
                continue

        # Default drawing without window clipping
        glColor3fv(color)
        if type_ == "POINT":
            glPointSize(5)
            glBegin(GL_POINTS)
            glVertex2f(*coords[0])
            glEnd()
        elif type_ == "LINE":
            glLineWidth(line_thickness)
            glBegin(GL_LINES)
            glVertex2f(*coords[0])
            glVertex2f(*coords[1])
            glEnd()
        elif type_ == "RECT":
            draw_rect(*coords[0], *coords[1])
        elif type_ == "ELLIPSE":
            x1, y1 = coords[0]
            x2, y2 = coords[1]
            draw_ellipse((x1 + x2) / 2, (y1 + y2) / 2, abs(x2 - x1) / 2, abs(y2 - y1) / 2)

    glutSwapBuffers()


def mouse_click(button, state, x, y):
    global mouse_clicks, clip_window, window_active, draw_mode
    global selected_index, temp_drag_start, is_dragging, temp_coords

    win_h = glutGet(GLUT_WINDOW_HEIGHT)
    y = win_h - y

    if draw_mode == "WINDOW":
        if state == GLUT_DOWN:
            mouse_clicks.append((x, y))
            if len(mouse_clicks) == 2:
                clip_window = [mouse_clicks[0], mouse_clicks[1]]
                window_active = True
                mouse_clicks.clear()
                draw_mode = "POINT"
                glutPostRedisplay()
        return

    if draw_mode == "SELECT" and state == GLUT_DOWN:
        selected_index = -1
        for i, obj in enumerate(objects):
            coords = obj['coords']
            type_ = obj['type']

            if type_ == "POINT":
                px, py = coords[0]
                if abs(px - x) <= 5 and abs(py - y) <= 5:
                    selected_index = i
                    break

            elif type_ in ["LINE", "RECT", "ELLIPSE"]:
                x1, y1 = coords[0]
                x2, y2 = coords[1]
                xmin, xmax = min(x1, x2), max(x1, x2)
                ymin, ymax = min(y1, y2), max(y1, y2)
                if xmin <= x <= xmax and ymin <= y <= ymax:
                    selected_index = i
                    break

        glutPostRedisplay()
        return

    if state == GLUT_DOWN:
        temp_drag_start = (x, y)
        is_dragging = True
        temp_coords.clear()
        temp_coords.append(temp_drag_start)

    elif state == GLUT_UP:
        is_dragging = False
        if draw_mode in ["LINE", "RECT", "ELLIPSE"]:
            start = temp_drag_start
            end = (x, y)
            if start != end:
                objects.append({
                    'type': draw_mode,
                    'coords': [start, end],
                    'color': current_color
                })
        elif draw_mode == "POINT":
            objects.append({
                'type': "POINT",
                'coords': [(x, y)],
                'color': current_color
            })
        temp_coords.clear()
        glutPostRedisplay()

def mouse_motion(x, y):
    global temp_coords
    if is_dragging and temp_coords:
        win_h = glutGet(GLUT_WINDOW_HEIGHT)
        y = win_h - y
        if len(temp_coords) == 1:
            temp_coords.append((x, y))
        else:
            temp_coords[1] = (x, y)
        glutPostRedisplay()

# Tambahkan bagian ini di fungsi keyboard()
def keyboard(key, x, y):
    global draw_mode, current_color, line_thickness, selected_index
    global transform_mode, window_active, clip_window

    key = key.decode('utf-8')

    if key == '1': draw_mode = "POINT"
    elif key == '2': draw_mode = "LINE"
    elif key == '3': draw_mode = "RECT"
    elif key == '4': draw_mode = "ELLIPSE"
    elif key == 'w': draw_mode = "WINDOW"
    elif key == 'v': draw_mode = "SELECT"
    elif key == 'r': current_color = colors['r']
    elif key == 'g': current_color = colors['g']
    elif key == 'b': current_color = colors['b']
    elif key in ['+', '=']:
        line_thickness += 1
    elif key in ['-', '_']:
        line_thickness = max(1, line_thickness - 1)
    elif key == 'n':
        if objects:
            selected_index = (selected_index + 1) % len(objects)
            print(f"🟢 Objek ke-{selected_index + 1} dipilih")
    elif key == 't':
        transform_mode = 't'
        print("Mode: Translasi")
    elif key == 'o':
        transform_mode = 'o'
        print("Mode: Rotasi")
    elif key == 's':
        transform_mode = 's'
        print("Mode: Skala")
    elif key == 'm':
        if 0 <= selected_index < len(objects):
            apply_transformation(objects[selected_index])
            print("Transformasi dijalankan")
    elif key == 'c':
        window_active = False
        clip_window.clear()
        print("❌ Clipping window dihapus")

    glutPostRedisplay()

def special_input(key, x, y):
    global clip_window
    if not window_active: return
    dx, dy = 10, 10
    if key == GLUT_KEY_LEFT:
        clip_window[0] = (clip_window[0][0] - dx, clip_window[0][1])
        clip_window[1] = (clip_window[1][0] - dx, clip_window[1][1])
    elif key == GLUT_KEY_RIGHT:
        clip_window[0] = (clip_window[0][0] + dx, clip_window[0][1])
        clip_window[1] = (clip_window[1][0] + dx, clip_window[1][1])
    elif key == GLUT_KEY_UP:
        clip_window[0] = (clip_window[0][0], clip_window[0][1] + dy)
        clip_window[1] = (clip_window[1][0], clip_window[1][1] + dy)
    elif key == GLUT_KEY_DOWN:
        clip_window[0] = (clip_window[0][0], clip_window[0][1] - dy)
        clip_window[1] = (clip_window[1][0], clip_window[1][1] - dy)
    glutPostRedisplay()

def reshape(key, x, y):
    global clip_window
    if not window_active: return
    delta = 10
    if key == b'[':
        clip_window[0] = (clip_window[0][0] + delta, clip_window[0][1] + delta)
        clip_window[1] = (clip_window[1][0] - delta, clip_window[1][1] - delta)
    elif key == b']':
        clip_window[0] = (clip_window[0][0] - delta, clip_window[0][1] - delta)
        clip_window[1] = (clip_window[1][0] + delta, clip_window[1][1] + delta)
    glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(window_width, window_height)
    glutCreateWindow(b"Grafika 2D Modul-A")
    glutDisplayFunc(display)
    glutMouseFunc(mouse_click)
    glutMotionFunc(mouse_motion)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_input)
    glutKeyboardUpFunc(reshape)
    init()
    glutMainLoop()


if __name__ == '__main__':
    main()