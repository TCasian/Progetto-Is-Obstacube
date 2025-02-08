import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from collections import deque
import torch.nn.functional as F

# Usa la GPU se disponibile
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class DQN(nn.Module):
    def __init__(self, state_shape, action_size, num_entity_types=5):
        super(DQN, self).__init__()
        self.embedding = nn.Embedding(num_entity_types, 4)
        self.conv1 = nn.Conv2d(4, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.spatial_attention = nn.Sequential(
            nn.Conv2d(32, 1, kernel_size=1),
            nn.Sigmoid()
        )
        self.fc1 = nn.Linear(32 * 20 * 20, 256)
        self.fc2 = nn.Linear(256, action_size)

        self._initialize_weights()

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')

                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)

    def forward(self, x):
        x = self.embedding(x.long())
        #print(f"Shape dopo embedding: {x.shape}")
        x = x.permute(0, 3, 1, 2)
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))

        attention = self.spatial_attention(x)
        x = x * attention

        x = x.flatten(start_dim=1)
        x = F.relu(self.fc1(x))
        return self.fc2(x)

class DQNAgent:
    def __init__(self, state_shape, action_size):
        self.state_shape = state_shape
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.997
        self.batch_size = 64
        self.learning_rate = 0.001

        self.model = DQN(state_shape, action_size).to(device)
        self.target_model = DQN(state_shape, action_size, num_entity_types=5).to(device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.criterion = nn.MSELoss()
        self.update_target_model()
        self.reward_normalizer = RewardNormalizer()

    def update_target_model(self):
        self.target_model.load_state_dict(self.model.state_dict())

    def preprocess_state(self, grid):

        # in array np
        grid = np.array(grid, dtype=np.int64)
        if grid.ndim > 2:
            grid = np.squeeze(grid) # squeeze dimensioni senno non va -> bug
        return np.where(np.isin(grid, [0, 1, 2, 3, 4, 5]), grid, 0)


    def remember(self, state, action, reward, next_state, done):
        processed_state = self.preprocess_state(state)
        processed_next_state = self.preprocess_state(next_state)
        self.memory.append((processed_state, action, reward, processed_next_state, done))

    def act(self, state):
        new_state = self.preprocess_state(state)  # Converti prima di passare alla rete
        state_tensor = torch.tensor(new_state, dtype=torch.long).unsqueeze(0).to(device)
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        with torch.no_grad():
            q_values = self.model(state_tensor)
        return torch.argmax(q_values).item()

    def replay(self):
        if len(self.memory) < self.batch_size:
            return
        minibatch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*minibatch)

        next_states = torch.tensor(np.array(next_states), dtype=torch.long).to(device)
        states = torch.tensor(np.array(states), dtype=torch.long).to(device)

        actions = torch.tensor(actions, dtype=torch.long).to(device)
        # Process rewards as NumPy array, normalize, then convert to tensor
        rewards_np = np.array(rewards, dtype=np.float32)
        rewards_np = self.reward_normalizer.normalize(rewards_np)
        rewards = torch.tensor(rewards_np, dtype=torch.float32).to(device)
        dones = torch.tensor(dones, dtype=torch.bool).to(device)

        q_values = self.model(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        with torch.no_grad():
            next_q_values = self.target_model(next_states).max(1)[0]
            target_q_values = rewards + (self.gamma * next_q_values * ~dones)

        loss = self.criterion(q_values, target_q_values)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()


    def save(self, name):
        torch.save(self.model.state_dict(), name)

    def load(self, name):
        self.model.load_state_dict(torch.load(name))
        self.model.to(device)


class RewardNormalizer:
    def __init__(self, clip_range=(-5.0, 5.0)):
        self.clip_range = clip_range
        self.mean = 0.0
        self.std = 1.0
        self.eps = 1e-8
        self.count = 1e-4

    def normalize(self, rewards):
        rewards = np.asarray(rewards)
        if len(rewards) > 1:
            # Update running statistics
            batch_mean = np.mean(rewards)
            batch_std = np.std(rewards) + self.eps
            batch_count = len(rewards)

            delta = batch_mean - self.mean
            total_count = self.count + batch_count

            # Update mean
            self.mean += delta * batch_count / total_count

            # Update variance
            m_a = self.std ** 2 * self.count
            m_b = batch_std ** 2 * batch_count
            M2 = m_a + m_b + delta ** 2 * self.count * batch_count / total_count
            self.std = np.sqrt(M2 / total_count)

            self.count = total_count

        # Normalize and clip
        normalized_rewards = (rewards - self.mean) / (self.std + self.eps)
        return np.clip(normalized_rewards, *self.clip_range)