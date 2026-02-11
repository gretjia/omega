# Filename: rq/trainer.py
# ROLE: The RQSDK-Powered Gym (v24 Maxwell)
# ADVANTAGE: Uses rq.data for consistent normalization & frozen stats

import torch
import torch.nn as nn
import torch.optim as optim
import joblib
import numpy as np
import pandas as pd
import os
import sys

# Import local interface
# Assumes running from root, or we add path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from rq.interface import OmegaRQ

# v24 Hyperparameters
INPUT_CHANNELS = 5
LOOKBACK_WINDOW = 120
LATENT_DIM = 16

class TCNBlock(nn.Module):
    def __init__(self, in_c, out_c, dilation):
        super().__init__()
        self.pad = 2 * dilation
        self.conv = nn.Conv1d(in_c, out_c, 3, padding=self.pad, dilation=dilation)
        self.relu = nn.LeakyReLU(0.1)
        
    def forward(self, x):
        out = self.conv(x)
        return self.relu(out[:, :, :-self.pad])

class MaxwellBrain(nn.Module):
    def __init__(self):
        super().__init__()
        # Encoder
        self.enc = nn.Sequential(
            TCNBlock(INPUT_CHANNELS, 16, 1),
            TCNBlock(16, 32, 2),
            TCNBlock(32, 64, 4)
        )
        # Bottleneck
        self.bottleneck = nn.Linear(64, LATENT_DIM)
        # Decoder
        self.from_latent = nn.Linear(LATENT_DIM, 64)
        self.dec = nn.Sequential(
            TCNBlock(64, 32, 1),
            TCNBlock(32, 16, 1),
            nn.Conv1d(16, INPUT_CHANNELS, 1)
        )

    def forward(self, x):
        x = x.permute(0, 2, 1)
        feats = self.enc(x)
        last_state = feats[:, :, -1] 
        z = self.bottleneck(last_state)
        z_expanded = self.from_latent(z).unsqueeze(2).expand(-1, -1, LOOKBACK_WINDOW)
        recon = self.dec(z_expanded)
        return recon.permute(0, 2, 1)

def train_maxwell():
    print(">>> RQSDK MAXWELL TRAINER (Full-Market Edition) <<<")
    OmegaRQ.init() # Load config
    
    # 1. Data Loading (The Golden Mine: history_ticks_full)
    data_dir = "d:/OMEGA/data/history_ticks_full"
    
    # Check cache first
    cache_file = "rq/maxwell_dataset_full.npy"
    if os.path.exists(cache_file):
        print(f"Loading cached dataset from {cache_file}...")
        X = np.load(cache_file)
    else:
        print(f"Scanning {data_dir} for tactical ticks...")
        files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
        
        # Parse codes and dates
        # Filename: Code_Date.csv (e.g. 000679_20250718.csv)
        tasks = []
        for f in files:
            parts = f.split('_')
            if len(parts) >= 2:
                code = parts[0]
                date_str = parts[1].replace('.csv', '')
                # Format date to YYYY-MM-DD
                if len(date_str) == 8:
                    date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
                    tasks.append((code, date))
        
        print(f"Found {len(tasks)} tactical sessions. Building tensors...")
        
        all_tensors = []
        # Limit for demo/memory safety? Let's take first 500 for now, or all if machine is big.
        # User said "Full Market", let's try to process a batch.
        MAX_SAMPLES = 2000 
        print(f"Processing top {MAX_SAMPLES} sessions...")
        
        processed_count = 0
        for code, date in tasks[:MAX_SAMPLES]:
            # We use get_maxwell_tensor but constrain it to that specific day
            # Adapter logic prioritizes history_ticks, but we need to point it to history_ticks_full?
            # Or we temporarily patch the adapter path?
            # Better: We read the file directly here to be 100% sure we use the golden data.
            # And we use OmegaRQ.data.stats to normalize.
            
            f_path = os.path.join(data_dir, f"{code}_{date.replace('-','')}.csv")
            try:
                # Direct read for speed and certainty
                df = pd.read_csv(f_path)
                
                # NO Mapping needed as CSVs are already in RQ format
                # Ensure 'last' exists
                if 'last' not in df.columns: 
                    # Try fallback if columns are different
                    if 'lastPrice' in df.columns:
                        df.rename(columns={'lastPrice': 'last', 'pvolume': 'volume'}, inplace=True)
                    else:
                        continue
                
                prices = df['last'].values
                vols = df['volume'].values
                
                # Feature Construction (Inline for speed)
                log_rets = np.zeros_like(prices)
                log_rets[1:] = np.log(prices[1:] / (prices[:-1] + 1e-9))
                log_vols = np.log1p(vols)
                
                # Rolling stats need pandas
                volatility = pd.Series(log_rets).rolling(10).std().fillna(0).values
                mom = pd.Series(prices).pct_change(10).fillna(0).values
                spread = np.zeros_like(prices) # Ignore spread for now if not reliable
                
                raw_features = np.column_stack([log_rets, log_vols, volatility, mom, spread])
                
                # Normalize using Frozen Stats
                norm_features = OmegaRQ.data.stats.normalize(raw_features)
                
                # Slice into windows
                if len(norm_features) > LOOKBACK_WINDOW:
                    # Stride for data augmentation?
                    stride = 10 
                    for i in range(0, len(norm_features) - LOOKBACK_WINDOW, stride):
                        all_tensors.append(norm_features[i:i+LOOKBACK_WINDOW])
                        
                processed_count += 1
                if processed_count % 100 == 0: print(f"... processed {processed_count} files")
                
            except Exception as e:
                # print(f"Error {f_path}: {e}")
                pass
                
        if not all_tensors:
            print("No valid data extracted.")
            return

        X = np.array(all_tensors)
        np.save(cache_file, X)
        print(f"Dataset cached to {cache_file}")

    print(f"Dataset Shape: {X.shape}")
    
    # 2. Train
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = MaxwellBrain().to(device)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()
    
    dataset = torch.utils.data.TensorDataset(torch.from_numpy(X).float().to(device))
    loader = torch.utils.data.DataLoader(dataset, batch_size=128, shuffle=True)
    
    model.train()
    for ep in range(10):
        total_loss = 0
        for b in loader:
            x = b[0]
            optimizer.zero_grad()
            recon = model(x)
            loss = criterion(recon, x)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {ep+1} Loss: {total_loss/len(loader):.6f}")
        
    # 3. Export
    # We save weights AND the stats from rq.data
    weights = {k: v.detach().cpu().numpy() for k, v in model.named_parameters()}
    weights['meta'] = OmegaRQ.data.stats.stats # Save the frozen stats used
    
    joblib.dump(weights, "rq/omega_brain_maxwell.pkl")
    print("✅ Brain Saved to rq/omega_brain_maxwell.pkl")

if __name__ == "__main__":
    train_maxwell()
