$fn = 36;

part = "print_layout";

body_length = 132;
body_width = 86;
deck_height = 24;
wall = 2.4;
floor_thickness = 2.4;
corner_radius = 8;

battery_length = 72;
battery_width = 38;
battery_height = 19;

pi_length = 65;
pi_width = 30;
pi_hole_dx = 58;
pi_hole_dy = 23;
pi_hole_d = 2.8;
standoff_d = 6.5;
standoff_h = 5;

driver_length = 44;
driver_width = 28;
driver_hole_dx = 36;
driver_hole_dy = 20;
driver_hole_d = 2.8;

sensor_plate_width = 56;
sensor_plate_height = 34;
sensor_plate_thickness = 3;

lid_height = 16;
lid_top = 2.4;

module rounded_box(size, r) {
    x = size[0];
    y = size[1];
    z = size[2];

    hull() {
        for (sx = [-1, 1]) {
            for (sy = [-1, 1]) {
                translate([sx * (x / 2 - r), sy * (y / 2 - r), 0])
                    cylinder(h = z, r = r);
            }
        }
    }
}

module screw_standoff(hole_d, outer_d, h) {
    difference() {
        cylinder(h = h, d = outer_d);
        translate([0, 0, -0.1]) cylinder(h = h + 0.2, d = hole_d);
    }
}

module slot(length, width, height) {
    hull() {
        translate([-(length / 2 - width / 2), 0, 0]) cylinder(h = height, d = width);
        translate([length / 2 - width / 2, 0, 0]) cylinder(h = height, d = width);
    }
}

module battery_cradle() {
    cradle_wall = 2;
    cradle_length = battery_length + 4;
    cradle_width = battery_width + 4;
    cradle_depth = battery_height + 2;

    difference() {
        translate([0, 0, floor_thickness])
            rounded_box([cradle_length, cradle_width, cradle_depth], 4);
        translate([0, 0, floor_thickness + cradle_wall])
            rounded_box(
                [cradle_length - cradle_wall * 2, cradle_width - cradle_wall * 2, cradle_depth],
                3
            );
        translate([cradle_length / 2 - 8, 0, floor_thickness + cradle_depth / 2])
            cube([10, 16, cradle_depth], center = true);
    }
}

module pi_mounts() {
    positions = [
        [-pi_hole_dx / 2, -pi_hole_dy / 2],
        [ pi_hole_dx / 2, -pi_hole_dy / 2],
        [-pi_hole_dx / 2,  pi_hole_dy / 2],
        [ pi_hole_dx / 2,  pi_hole_dy / 2]
    ];

    for (pos = positions) {
        translate([pos[0], pos[1], floor_thickness])
            screw_standoff(pi_hole_d, standoff_d, standoff_h);
    }
}

module driver_mounts() {
    positions = [
        [-driver_hole_dx / 2, -driver_hole_dy / 2],
        [ driver_hole_dx / 2, -driver_hole_dy / 2],
        [-driver_hole_dx / 2,  driver_hole_dy / 2],
        [ driver_hole_dx / 2,  driver_hole_dy / 2]
    ];

    for (pos = positions) {
        translate([pos[0], pos[1], floor_thickness])
            screw_standoff(driver_hole_d, standoff_d, standoff_h);
    }
}

module deck_shell() {
    difference() {
        rounded_box([body_length, body_width, deck_height], corner_radius);
        translate([0, 0, floor_thickness])
            rounded_box(
                [body_length - wall * 2, body_width - wall * 2, deck_height],
                corner_radius - wall
            );

        translate([body_length / 2 - wall / 2, 0, deck_height / 2 + 2])
            cube([10, 18, 12], center = true);

        translate([-body_length / 2 + 8, 0, deck_height / 2 + 2])
            cube([8, 24, 10], center = true);
    }
}

module deck() {
    union() {
        difference() {
            deck_shell();

            translate([0, body_width / 2 - wall / 2, 12])
                cube([sensor_plate_width + 6, 12, 18], center = true);

            for (x = [-38, -20, -2, 16, 34]) {
                translate([x, 0, floor_thickness / 2])
                    cube([4, body_width - 18, floor_thickness + 0.4], center = true);
            }
        }

        translate([-18, 0, 0]) battery_cradle();
        translate([30, 16, 0]) pi_mounts();
        translate([26, -22, 0]) driver_mounts();

        translate([48, -body_width / 2 + wall + 8, floor_thickness])
            cube([16, 6, 8]);

        translate([-48, body_width / 2 - wall - 7, floor_thickness])
            cube([18, 6, 8]);

        translate([0, body_width / 2 - wall - 2.5, floor_thickness + 3])
            cube([sensor_plate_width + 10, 3, 8], center = true);
    }
}

module lid_tabs() {
    for (x = [-38, 38]) {
        translate([x, body_width / 2 - wall - 2.8, 0]) cube([12, 5, 5], center = true);
        translate([x, -body_width / 2 + wall + 2.8, 0]) cube([12, 5, 5], center = true);
    }
}

module lid() {
    outer_h = lid_height;

    difference() {
        union() {
            difference() {
                rounded_box([body_length - 1.2, body_width - 1.2, outer_h], corner_radius - 1);
                translate([0, 0, lid_top])
                    rounded_box(
                        [body_length - wall * 2 - 1.2, body_width - wall * 2 - 1.2, outer_h],
                        corner_radius - wall - 1
                    );
            }
            translate([0, 0, 5]) lid_tabs();
        }

        translate([body_length / 2 - 4, 0, outer_h / 2])
            cube([10, 16, 12], center = true);

        for (x = [-34, -22, -10, 2, 14, 26]) {
            translate([x, 0, -0.1]) slot(28, 3, lid_top + 0.2);
        }

        translate([34, 16, -0.1]) cube([18, 14, lid_top + 0.2], center = true);
        translate([26, -22, -0.1]) cube([20, 16, lid_top + 0.2], center = true);
    }
}

module sensor_plate() {
    difference() {
        rounded_box([sensor_plate_width, sensor_plate_thickness, sensor_plate_height], 3);

        for (x = [-18, 18]) {
            translate([x, 0, 0]) rotate([90, 0, 0])
                cylinder(h = sensor_plate_thickness + 0.2, d = 3.2, center = true);
        }

        translate([0, 0, 8]) rotate([90, 0, 0])
            slot(18, 3.2, sensor_plate_thickness + 0.2);
        translate([0, 0, -8]) rotate([90, 0, 0])
            slot(18, 3.2, sensor_plate_thickness + 0.2);

        translate([0, 0, 0]) rotate([90, 0, 0])
            cube([24, sensor_plate_height - 8, sensor_plate_thickness + 0.2], center = true);
    }
}

module charger_bracket() {
    bracket_length = 30;
    bracket_width = 18;
    bracket_height = 10;

    difference() {
        union() {
            cube([bracket_length, bracket_width, 2.4]);
            translate([0, 0, 2.4]) cube([2.4, bracket_width, bracket_height]);
            translate([bracket_length - 2.4, 0, 2.4]) cube([2.4, bracket_width, bracket_height]);
        }

        translate([8, bracket_width / 2, -0.1]) cylinder(h = 3, d = 2.8);
        translate([bracket_length - 8, bracket_width / 2, -0.1]) cylinder(h = 3, d = 2.8);
        translate([bracket_length / 2, bracket_width / 2, 7]) cube([14, 8, 8], center = true);
    }
}

module print_layout() {
    translate([-78, 0, 0]) deck();
    translate([80, 0, 0]) lid();
    translate([0, -70, 0]) sensor_plate();
    translate([0, 48, 0]) charger_bracket();
}

if (part == "deck") {
    deck();
} else if (part == "lid") {
    lid();
} else if (part == "sensor_plate") {
    sensor_plate();
} else if (part == "charger_bracket") {
    charger_bracket();
} else {
    print_layout();
}
