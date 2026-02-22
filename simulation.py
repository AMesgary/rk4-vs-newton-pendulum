import sys
import math
import pygame

class newtons_pendulum:
    def __init__(self, length=150, mass=1.0, gravity=9.81, damping=0.0, initial_angle=math.pi/3, initial_velocity=0):
        self.L = length
        self.L_real = 1.0
        self.m = mass
        self.g = gravity
        self.b = damping
        self.theta = initial_angle
        self.omega = initial_velocity
        self.alpha = 0
        self.time = 0
        self.dt = 0.032

        self.history_time = []
        self.history_theta = []
        self.history_omega = []
        self.history_energy = []

    def calculate_forces(self):
        tangential_force = -self.m * self.g * math.sin(self.theta)
        linear_velocity = self.L_real * self.omega
        damping_force = -self.b * linear_velocity
        return tangential_force + damping_force

    def update_physics(self):
        net_force = self.calculate_forces()
        self.alpha = net_force / (self.m * self.L_real)
        self.omega += self.alpha * self.dt
        self.theta += self.omega * self.dt
        self.time += self.dt

        self.history_time.append(self.time)
        self.history_theta.append(self.theta)
        self.history_omega.append(self.omega)

        kinetic = 0.5 * self.m * (self.L_real * self.omega)**2
        potential = self.m * self.g * self.L_real * (1 - math.cos(self.theta))
        self.history_energy.append(kinetic + potential)

    def cartesian_pos(self, center_x, center_y):
        x = center_x + self.L * math.sin(self.theta)
        y = center_y + self.L * math.cos(self.theta)
        return int(x), int(y)

    def reset(self, angle, velocity):
        self.theta = angle
        self.omega = velocity
        self.alpha = 0
        self.time = 0
        self.history_time.clear()
        self.history_theta.clear()
        self.history_omega.clear()
        self.history_energy.clear()

class differential_pendulum:
    def __init__(self, length=150, mass=1.0, gravity=9.81, damping=0.0, initial_angle=math.pi/3, initial_velocity=0):
        self.L = length
        self.L_real = 1.0
        self.m = mass
        self.g = gravity
        self.b = damping
        self.theta = initial_angle
        self.omega = initial_velocity
        self.time = 0
        self.dt = 0.032

        self.history_time = []
        self.history_theta = []
        self.history_omega = []
        self.history_energy = []

    def acceleration(self, theta, omega):
        return -(self.g / self.L_real) * math.sin(theta) - (self.b / self.m) * omega

    def update_rk4(self):
        k1_theta = self.omega
        k1_omega = self.acceleration(self.theta, self.omega)

        k2_theta = self.omega + 0.5 * self.dt * k1_omega
        k2_omega = self.acceleration(self.theta + 0.5 * self.dt * k1_theta, self.omega + 0.5 * self.dt * k1_omega)

        k3_theta = self.omega + 0.5 * self.dt * k2_omega
        k3_omega = self.acceleration(self.theta + 0.5 * self.dt * k2_theta, self.omega + 0.5 * self.dt * k2_omega)

        k4_theta = self.omega + self.dt * k3_omega
        k4_omega = self.acceleration(self.theta + self.dt * k3_theta, self.omega + self.dt * k3_omega)

        self.theta += (self.dt / 6) * (k1_theta + 2*k2_theta + 2*k3_theta + k4_theta)
        self.omega += (self.dt / 6) * (k1_omega + 2*k2_omega + 2*k3_omega + k4_omega)
        self.time += self.dt

        self.history_time.append(self.time)
        self.history_theta.append(self.theta)
        self.history_omega.append(self.omega)

        kinetic = 0.5 * self.m * (self.L_real * self.omega)**2
        potential = self.m * self.g * self.L_real * (1 - math.cos(self.theta))
        self.history_energy.append(kinetic + potential)

    def cartesian_pos(self, center_x, center_y):
        x = center_x + self.L * math.sin(self.theta)
        y = center_y + self.L * math.cos(self.theta)
        return int(x), int(y)

    def reset(self, angle, velocity):
        self.theta = angle
        self.omega = velocity
        self.time = 0
        self.history_time.clear()
        self.history_theta.clear()
        self.history_omega.clear()
        self.history_energy.clear()

def draw_comparison_plot(screen, newton_pendulum, diff_pendulum, x_offset, y_offset, width=400, height=200):
    plot_rect = pygame.Rect(x_offset, y_offset, width, height)
    pygame.draw.rect(screen, (240, 240, 240), plot_rect)
    pygame.draw.rect(screen, (0, 0, 0), plot_rect, 2)

    font_small = pygame.font.Font(None, 16)
    font_title = pygame.font.Font(None, 18)
    font_axis = pygame.font.Font(None, 14)

    if len(newton_pendulum.history_time) > 2 and len(diff_pendulum.history_time) > 2:
        max_time = max(newton_pendulum.time, diff_pendulum.time)
        time_window = 15
        min_time = max(0, max_time - time_window)

        all_angles = []
        for i, t in enumerate(newton_pendulum.history_time):
            if t >= min_time:
                all_angles.append(math.degrees(newton_pendulum.history_theta[i]))
        for i, t in enumerate(diff_pendulum.history_time):
            if t >= min_time:
                all_angles.append(math.degrees(diff_pendulum.history_theta[i]))

        if all_angles:
            min_angle = min(all_angles)
            max_angle = max(all_angles)
            angle_range = max_angle - min_angle
            if angle_range < 10:
                center = (max_angle + min_angle) / 2
                min_angle = center - 5
                max_angle = center + 5
                angle_range = 10

            newton_points = []
            for i, t in enumerate(newton_pendulum.history_time):
                if t >= min_time and i > 0:
                    x = x_offset + int((t - min_time) / time_window * (width - 80)) + 50
                    angle_deg = math.degrees(newton_pendulum.history_theta[i])
                    y = y_offset + height - 50 - int((angle_deg - min_angle) / angle_range * (height - 80))
                    newton_points.append((x, y))

            if len(newton_points) > 1:
                temp_surface = pygame.Surface((width, height))
                temp_surface.set_alpha(128)
                temp_surface.fill((240, 240, 240))
                pygame.draw.lines(temp_surface, (255, 0, 0), False,
                                [(p[0] - x_offset, p[1] - y_offset) for p in newton_points], 2)
                screen.blit(temp_surface, (x_offset, y_offset))

            diff_points = []
            for i, t in enumerate(diff_pendulum.history_time):
                if t >= min_time and i > 0:
                    x = x_offset + int((t - min_time) / time_window * (width - 80)) + 50
                    angle_deg = math.degrees(diff_pendulum.history_theta[i])
                    y = y_offset + height - 50 - int((angle_deg - min_angle) / angle_range * (height - 80))
                    diff_points.append((x, y))

            if len(diff_points) > 1:
                temp_surface = pygame.Surface((width, height))
                temp_surface.set_alpha(128)
                temp_surface.fill((240, 240, 240))
                pygame.draw.lines(temp_surface, (0, 0, 255), False,
                                [(p[0] - x_offset, p[1] - y_offset) for p in diff_points], 2)
                screen.blit(temp_surface, (x_offset, y_offset))

            pygame.draw.line(screen, (0, 0, 0), (x_offset + 50, y_offset + 30), (x_offset + 50, y_offset + height - 30), 2)
            pygame.draw.line(screen, (0, 0, 0), (x_offset + 50, y_offset + height - 30), (x_offset + width - 30, y_offset + height - 30), 2)

            y_ticks = 5
            for i in range(y_ticks + 1):
                angle_val = min_angle + (max_angle - min_angle) * i / y_ticks
                y_pos = y_offset + height - 30 - int(i / y_ticks * (height - 60))

                pygame.draw.line(screen, (0, 0, 0), (x_offset + 45, y_pos), (x_offset + 50, y_pos), 1)

                label = font_axis.render(f"{angle_val:.1f}°", True, (0, 0, 0))
                label_rect = label.get_rect(right=x_offset + 43, centery=y_pos)
                screen.blit(label, label_rect)

            x_ticks = 4
            for i in range(x_ticks + 1):
                time_val = min_time + time_window * i / x_ticks
                x_pos = x_offset + 50 + int(i / x_ticks * (width - 80))

                pygame.draw.line(screen, (0, 0, 0), (x_pos, y_offset + height - 30), (x_pos, y_offset + height - 25), 1)

                label = font_axis.render(f"{time_val:.1f}s", True, (0, 0, 0))
                label_rect = label.get_rect(centerx=x_pos, top=y_offset + height - 23)
                screen.blit(label, label_rect)

            title = font_title.render("MOTION COMPARISON", True, (0, 0, 0))
            screen.blit(title, (x_offset + 5, y_offset + 5))

            newton_legend = font_small.render("red: NEWTON", True, (255, 0, 0))
            screen.blit(newton_legend, (x_offset + 150, y_offset + 5))

            diff_legend = font_small.render("blue: DIFF EQ", True, (0, 0, 255))
            screen.blit(diff_legend, (x_offset + 250, y_offset + 5))

def phase_space_plot(screen, newton_pendulum, diff_pendulum, x_offset, y_offset, width=400, height=200):
    plot_rect = pygame.Rect(x_offset, y_offset, width, height)
    pygame.draw.rect(screen, (240, 240, 240), plot_rect)
    pygame.draw.rect(screen, (0, 0, 0), plot_rect, 2)

    font_small = pygame.font.Font(None, 16)
    font_title = pygame.font.Font(None, 18)
    font_axis = pygame.font.Font(None, 14)

    if len(newton_pendulum.history_theta) > 2 and len(diff_pendulum.history_theta) > 2:
        all_thetas = []
        all_omegas = []

        points_to_show = min(500, len(newton_pendulum.history_theta))
        start_idx = max(0, len(newton_pendulum.history_theta) - points_to_show)

        for i in range(start_idx, len(newton_pendulum.history_theta)):
            all_thetas.append(newton_pendulum.history_theta[i])
            all_omegas.append(newton_pendulum.history_omega[i])

        points_to_show_diff = min(500, len(diff_pendulum.history_theta))
        start_idx_diff = max(0, len(diff_pendulum.history_theta) - points_to_show_diff)

        for i in range(start_idx_diff, len(diff_pendulum.history_theta)):
            all_thetas.append(diff_pendulum.history_theta[i])
            all_omegas.append(diff_pendulum.history_omega[i])

        if all_thetas and all_omegas:
            min_theta = min(all_thetas)
            max_theta = max(all_thetas)
            min_omega = min(all_omegas)
            max_omega = max(all_omegas)

            theta_range = max_theta - min_theta
            omega_range = max_omega - min_omega

            if theta_range < 0.1:
                center_theta = (max_theta + min_theta) / 2
                min_theta = center_theta - 0.1
                max_theta = center_theta + 0.1
                theta_range = 0.2

            if omega_range < 0.1:
                center_omega = (max_omega + min_omega) / 2
                min_omega = center_omega - 0.1
                max_omega = center_omega + 0.1
                omega_range = 0.2

            newton_points = []
            points_to_show = min(500, len(newton_pendulum.history_theta))
            start_idx = max(0, len(newton_pendulum.history_theta) - points_to_show)

            for i in range(start_idx, len(newton_pendulum.history_theta)):
                theta = newton_pendulum.history_theta[i]
                omega = newton_pendulum.history_omega[i]
                x = x_offset + 50 + int((theta - min_theta) / theta_range * (width - 80))
                y = y_offset + height - 50 - int((omega - min_omega) / omega_range * (height - 80))
                newton_points.append((x, y))

            if len(newton_points) > 1:
                temp_surface = pygame.Surface((width, height))
                temp_surface.set_alpha(150)
                temp_surface.fill((240, 240, 240))
                pygame.draw.lines(temp_surface, (255, 0, 0), False, [(p[0] - x_offset, p[1] - y_offset) for p in newton_points], 2)
                screen.blit(temp_surface, (x_offset, y_offset))

            diff_points = []
            points_to_show = min(500, len(diff_pendulum.history_theta))
            start_idx = max(0, len(diff_pendulum.history_theta) - points_to_show)

            for i in range(start_idx, len(diff_pendulum.history_theta)):
                theta = diff_pendulum.history_theta[i]
                omega = diff_pendulum.history_omega[i]
                x = x_offset + 50 + int((theta - min_theta) / theta_range * (width - 80))
                y = y_offset + height - 50 - int((omega - min_omega) / omega_range * (height - 80))
                diff_points.append((x, y))

            if len(diff_points) > 1:
                temp_surface = pygame.Surface((width, height))
                temp_surface.set_alpha(150)
                temp_surface.fill((240, 240, 240))
                pygame.draw.lines(temp_surface, (0, 0, 255), False, [(p[0] - x_offset, p[1] - y_offset) for p in diff_points], 2)
                screen.blit(temp_surface, (x_offset, y_offset))

            pygame.draw.line(screen, (0, 0, 0), (x_offset + 50, y_offset + 30), (x_offset + 50, y_offset + height - 30), 2)
            pygame.draw.line(screen, (0, 0, 0), (x_offset + 50, y_offset + height - 30), (x_offset + width - 30, y_offset + height - 30), 2)

            y_ticks = 5
            for i in range(y_ticks + 1):
                omega_val = min_omega + (max_omega - min_omega) * i / y_ticks
                y_pos = y_offset + height - 30 - int(i / y_ticks * (height - 60))

                pygame.draw.line(screen, (0, 0, 0), (x_offset + 45, y_pos), (x_offset + 50, y_pos), 1)

                label = font_axis.render(f"{omega_val:.2f}", True, (0, 0, 0))
                label_rect = label.get_rect(right=x_offset + 43, centery=y_pos)
                screen.blit(label, label_rect)

            x_ticks = 5
            for i in range(x_ticks + 1):
                theta_val = min_theta + (max_theta - min_theta) * i / x_ticks
                x_pos = x_offset + 50 + int(i / x_ticks * (width - 80))

                pygame.draw.line(screen, (0, 0, 0), (x_pos, y_offset + height - 30), (x_pos, y_offset + height - 25), 1)

                label = font_axis.render(f"{theta_val:.2f}", True, (0, 0, 0))
                label_rect = label.get_rect(centerx=x_pos, top=y_offset + height - 23)
                screen.blit(label, label_rect)

            title = font_title.render("PHASE SPACE (ω vs θ)", True, (0, 0, 0))
            screen.blit(title, (x_offset + 5, y_offset + 5))

            newton_legend = font_small.render("red: NEWTON", True, (255, 0, 0))
            screen.blit(newton_legend, (x_offset + 150, y_offset + 5))

            diff_legend = font_small.render("blue: DIFF EQ", True, (0, 0, 255))
            screen.blit(diff_legend, (x_offset + 250, y_offset + 5))

            x_label = font_small.render("θ (rad)", True, (0, 0, 0))
            screen.blit(x_label, (x_offset + width - 50, y_offset + height - 15))

            y_label = font_small.render("ω (rad/s)", True, (0, 0, 0))
            screen.blit(y_label, (x_offset + 5, y_offset + 15))

def draw_pendulum(screen, pendulum, mass, center_x, center_y, color, label):
    pygame.draw.circle(screen, (0, 0, 0), (center_x, center_y), 8)
    pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), 5)

    bob_x, bob_y = pendulum.cartesian_pos(center_x, center_y)

    pygame.draw.line(screen, (128, 128, 128), (center_x, center_y), (bob_x, bob_y), 3)

    pygame.draw.circle(screen, color, (bob_x, bob_y), 12*math.sqrt(mass)+2)

    font = pygame.font.Font(None, 22)
    label_surface = font.render(label, True, color)
    label_rect = label_surface.get_rect(center=(center_x, center_y - 50))
    screen.blit(label_surface, label_rect)

def calculate_difference(newton_pendulum, diff_pendulum):
    if len(newton_pendulum.history_theta) > 0 and len(diff_pendulum.history_theta) > 0:
        angle_diff = abs(math.degrees(newton_pendulum.theta - diff_pendulum.theta))
        omega_diff = abs(newton_pendulum.omega - diff_pendulum.omega)
        return angle_diff, omega_diff
    return 0, 0

def main():
    pygame.init()

    WIDTH, HEIGHT = 1600, 900
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    GREEN = (0, 180, 0)
    DARK_GRAY = (64, 64, 64)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("differential equations: pendulum comparison - by ARMAN MESGARY")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 28)
    font_small = pygame.font.Font(None, 24)
    font_tiny = pygame.font.Font(None, 22)

    initial_angle = math.pi/4
    initial_velocity = 0
    damping = 0.05
    gravity = 9.81
    length = 150
    mass = 1.0

    newton_pendulum = newtons_pendulum(length=length, mass=mass, gravity=gravity, damping=damping, initial_angle=initial_angle, initial_velocity=initial_velocity)
    diff_pendulum = differential_pendulum(length=length, mass=mass, gravity=gravity, damping=damping, initial_angle=initial_angle, initial_velocity=initial_velocity)

    paused = False
    show_plot = True
    show_phase = True

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    newton_pendulum.reset(initial_angle, initial_velocity)
                    diff_pendulum.reset(initial_angle, initial_velocity)
                elif event.key == pygame.K_p:
                    show_plot = not show_plot
                elif event.key == pygame.K_q:
                    show_phase = not show_phase
                elif event.key == pygame.K_g:
                    gravity = min(gravity + 0.5, 20.0)
                    newton_pendulum.g = gravity
                    diff_pendulum.g = gravity
                elif event.key == pygame.K_h:
                    gravity = max(gravity - 0.5, 1.0)
                    newton_pendulum.g = gravity
                    diff_pendulum.g = gravity
                elif event.key == pygame.K_l:
                    length = min(length + 10, 300)
                    newton_pendulum.L = length
                    diff_pendulum.L = length
                    newton_pendulum.L_real = length / 150.0
                    diff_pendulum.L_real = length / 150.0
                elif event.key == pygame.K_k:
                    length = max(length - 10, 50)
                    newton_pendulum.L = length
                    diff_pendulum.L = length
                    newton_pendulum.L_real = length / 150.0
                    diff_pendulum.L_real = length / 150.0
                elif event.key == pygame.K_m:
                    mass = min(mass + 0.1, 5.0)
                    newton_pendulum.m = mass
                    diff_pendulum.m = mass
                elif event.key == pygame.K_n:
                    mass = max(mass - 0.1, 0.1)
                    newton_pendulum.m = mass
                    diff_pendulum.m = mass
                elif event.key == pygame.K_UP:
                    damping = min(damping + 0.01, 0.5)
                    newton_pendulum.b = damping
                    diff_pendulum.b = damping
                elif event.key == pygame.K_DOWN:
                    damping = max(damping - 0.01, 0.0)
                    newton_pendulum.b = damping
                    diff_pendulum.b = damping

        if not paused:
            newton_pendulum.update_physics()
            diff_pendulum.update_rk4()

        screen.fill(WHITE)

        title = font.render("PENDULUM COMPARISON: NEWTON'S LAWS vs DIFFERENTIAL EQUATIONS", True, BLACK)
        title_rect = title.get_rect(center=(WIDTH//2, 25))
        screen.blit(title, title_rect)

        newton_center = (350, 180)
        diff_center = (650, 180)

        draw_pendulum(screen, newton_pendulum, newton_pendulum.m, newton_center[0], newton_center[1], RED, "NEWTON'S LAWS")
        draw_pendulum(screen, diff_pendulum, diff_pendulum.m, diff_center[0], diff_center[1], BLUE, "DIFFERENTIAL EQ.")

        y_start = 550
        newton_info = [
            "NEWTON'S LAWS METHOD:",
            f"angle: {math.degrees(newton_pendulum.theta):.2f}°",
            f"angular velocity: {newton_pendulum.omega:.3f} rad/s",
            f"angular acceleration: {newton_pendulum.alpha:.3f} rad/s²",
            f"time: {newton_pendulum.time:.2f}s"
        ]

        for i, text in enumerate(newton_info):
            color = RED if i == 0 else BLACK
            weight = font if i == 0 else font_small
            rendered = weight.render(text, True, color)
            screen.blit(rendered, (30, y_start + i * 22))

        diff_info = [
            "DIFFERENTIAL EQUATION METHOD:",
            f"angle: {math.degrees(diff_pendulum.theta):.2f}°",
            f"angular velocity: {diff_pendulum.omega:.3f} rad/s",
            f"time: {diff_pendulum.time:.2f}s",
            "equation: d²θ/dt² = -(g/L)sin(θ) - (b/m)dθ/dt"
        ]

        for i, text in enumerate(diff_info):
            color = BLUE if i == 0 else BLACK
            weight = font if i == 0 else font_small
            rendered = weight.render(text, True, color)
            screen.blit(rendered, (475, y_start + i * 22))

        angle_diff, omega_diff = calculate_difference(newton_pendulum, diff_pendulum)

        comparison_info = [
            "COMPARISON:",
            f"angle difference: {angle_diff:.4f}°",
            f"velocity difference: {omega_diff:.4f} rad/s"
        ]

        for i, text in enumerate(comparison_info):
            color = GREEN if i == 0 else BLACK
            weight = font if i == 0 else font_small
            rendered = weight.render(text, True, color)
            screen.blit(rendered, (950, y_start + i * 22))

        params_y = HEIGHT - 180
        parameter_info = [
            "CURRENT PARAMETERS:",
            f"gravity: {gravity:.1f} m/s²",
            f"length: {length} px ({length/150:.2f}m)",
            f"mass: {mass:.1f} kg",
            f"damping: {damping:.3f}"
        ]

        for i, text in enumerate(parameter_info):
            color = DARK_GRAY if i == 0 else BLACK
            weight = font if i == 0 else font_small
            rendered = weight.render(text, True, color)
            screen.blit(rendered, (475, params_y + i * 22))

        controls_y = HEIGHT - 180

        controls = [
            "CONTROLS:",
            "SPACE: pause/resume    R: reset",
            "P: toggle time plot    Q: toggle phase plot",
            "",
            "PARAMETER CONTROLS:",
            "UP/DOWN: damping (0.0-0.5)",
            "G/H: gravity (1.0-20.0 m/s²)",
            "L/K: length (50-300 px)",
            "M/N: mass (0.1-5.0 kg)"
        ]

        for i, instruction in enumerate(controls):
            color = GREEN if i == 0 or i == 4 else BLACK
            weight = font if i == 0 or i == 4 else font_tiny
            text = weight.render(instruction, True, color)
            screen.blit(text, (30, controls_y + i * 18))

        plot_width = 400
        plot_height = 200

        if show_plot and show_phase and len(newton_pendulum.history_time) > 10:
            plot_x = WIDTH - 650
            plot_y = 60
            draw_comparison_plot(screen, newton_pendulum, diff_pendulum, plot_x, plot_y, 600, 180)

            phase_x = WIDTH - 650
            phase_y = 260
            phase_space_plot(screen, newton_pendulum, diff_pendulum, phase_x, phase_y, 600, 180)
        elif show_plot and len(newton_pendulum.history_time) > 10:
            plot_x = WIDTH - 650
            plot_y = 100
            draw_comparison_plot(screen, newton_pendulum, diff_pendulum, plot_x, plot_y, 600, 300)
        elif show_phase and len(newton_pendulum.history_time) > 10:
            phase_x = WIDTH - 650
            phase_y = 100
            phase_space_plot(screen, newton_pendulum, diff_pendulum, phase_x, phase_y, 600, 300)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

