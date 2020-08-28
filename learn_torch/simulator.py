import numpy as np
import torch

import gym
import matplotlib
import matplotlib.pyplot as plt
import torchvision.transforms as T
from PIL import Image   # python image library
import itertools

import dqn


# ipython
is_ipython = 'inline' in matplotlib.get_backend()
if is_ipython:
    from IPython import display


plt.ion()
device = torch.device("cpu")


def get_cart_location(screen_width):
    world_width = env.x_threshold * 2
    scale = screen_width / world_width
    return int(env.state[0] * scale + screen_width / 2.0)  # MIDDLE OF CART


def get_screen():
    # Returned screen requested by gym is 400x600x3, but is sometimes larger
    # such as 800x1200x3. Transpose it into torch order (CHW).
    screen = env.render(mode='rgb_array').transpose((2, 0, 1))
    # Cart is in the lower half, so strip off the top and bottom of the screen
    _, screen_height, screen_width = screen.shape
    screen = screen[:, int(screen_height*0.4):int(screen_height * 0.8)]
    view_width = int(screen_width * 0.6)
    cart_location = get_cart_location(screen_width)
    if cart_location < view_width // 2:
        slice_range = slice(view_width)
    elif cart_location > (screen_width - view_width // 2):
        slice_range = slice(-view_width, None)
    else:
        slice_range = slice(cart_location - view_width // 2,
                            cart_location + view_width // 2)
    # Strip off the edges, so that we have a square image centered on a cart
    screen = screen[:, :, slice_range]
    # Convert to float, rescale, convert to torch tensor
    # (this doesn't require a copy)
    screen = np.ascontiguousarray(screen, dtype=np.float32) / 255
    screen = torch.from_numpy(screen)
    # Resize, and add a batch dimension (BCHW)
    resize = T.Compose([T.ToPILImage(),
                        T.Resize(40, interpolation=Image.CUBIC),
                        T.ToTensor()])
    return resize(screen).unsqueeze(0).to(device)


class DurationAccumulator(object):
    def __init__(self):
        self.episode_durations = []

    def add_episode(self, duration):
        self.episode_durations.append(duration)

    def plot_durations(self, is_ipython):
        plt.figure(2)
        plt.clf()
        durations_t = torch.tensor(self.episode_durations, dtype=torch.float)
        plt.title('Training...')
        plt.xlabel('Episode')
        plt.ylabel('Duration')
        plt.plot(durations_t.numpy())
        # Take 100 episode averages and plot them too
        if len(durations_t) >= 100:
            means = durations_t.unfold(0, 100, 1).mean(1).view(-1)
            means = torch.cat((torch.zeros(99), means))
            plt.plot(means.numpy())

        plt.pause(0.001)  # pause a bit so that plots are updated
        if is_ipython:
            display.clear_output(wait=True)
            display.display(plt.gcf())


TARGET_UPDATE = 10

def simulation(num_episodes, model, memory):
    duration_acc = DurationAccumulator()
    for i_episode in range(num_episodes):
        # Initialize the environment and state
        env.reset()
        last_screen = get_screen()
        current_screen = get_screen()
        state = current_screen - last_screen
        for t in itertools.count():
            # Select and perform an action
            action = model.select_action(state)
            _, reward, done, _ = env.step(action.item())
            reward = torch.tensor([reward], device=device)

            # Observe new state
            last_screen = current_screen
            current_screen = get_screen()
            if not done:
                next_state = current_screen - last_screen
            else:
                next_state = None

            # Store the transition in memory
            memory.push(state, action, next_state, reward)

            # Move to the next state
            state = next_state

            # Perform one step of the optimization (on the target network)
            model.optimize_model()
            if done:
                duration_acc.add_episode(t + 1)
                duration_acc.plot_durations(is_ipython)
                break
        # Update the target network, copying all weights and biases in DQN
        if i_episode % TARGET_UPDATE == 0:
            model.update_model()

if __name__ == "__main__":
    env = gym.make('CartPole-v0').unwrapped

    env.reset()
    plt.figure()
    plt.imshow(get_screen().cpu().squeeze(0).permute(1, 2, 0).numpy(),
              interpolation='none')
    plt.title('Example extracted screen')
    plt.show()

    init_screen = get_screen()
    _, _, screen_height, screen_width = init_screen.shape
    # Get number of actions from gym action space
    n_actions = env.action_space.n

    memory = dqn.ReplayMemory(10000)

    simulation(150, dqn.DQNModel(screen_height, screen_width, n_actions, memory, device), memory)

    print('Complete')
    env.render()
    env.close()
    plt.ioff()
    plt.show()