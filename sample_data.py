sample_grades = {
    "Akash": [(20, 88), (30, 92)],
    "Keya": [(25, 90), (25, 95)],
    "Jamal": [(30, 70), (30, 82)],
    "Emily": [(40, 85), (20, 78)],
    "Li Wei": [(30, 93), (20, 89)],
    "Aisha": [(25, 80), (25, 85)],
    "Ryan": [(35, 76), (30, 81)],
    "Priya": [(20, 91), (30, 94)],
    "Marcus": [(25, 68), (35, 73)],
    "Sakura": [(30, 88), (25, 90)],
}

sample_passwords = {
    name: name.lower().replace(" ", "") + "123"
    for name in sample_grades
}
