'''
https://guyuena.github.io/PyTorch-study-Tutorials/beginner/transformer_tutorial.html
'''
import math
from typing import Tuple

import torch
from torch import nn, Tensor
import torch.nn.functional as F
from torch.nn import TransformerEncoder, TransformerEncoderLayer
from torch.utils.data import dataset

import datasets
from torchtext.datasets import WikiText2
from torchtext.data.utils import get_tokenizer
from torchtext.vocab import build_vocab_from_iterator

from collections import defaultdict

import copy
import time


bptt = 35
device = None


class BigramModel(object):
    def __init__(self, ntokens: int) -> None:
        self.token_num = ntokens
        self._is_training = True
        self._bigram_counts = torch.zeros(ntokens, ntokens, dtype=torch.int32)

    def train(self):
        self._is_training = True

    def eval(self):
        self._is_training = False

    def infer(self, src: Tensor) -> Tensor:
        ps = self._bigram_counts[src]
        div = ps.sum(-1).clip(min=1)
        ps = ps / div.unsqueeze(-1)
        eps = 1 / self.token_num * 0.001
        ps.clip_(min=eps, max=1-eps)
        return torch.log(ps / (1 - ps))

    def count(self, src: Tensor) -> Tensor:
        self._bigram_counts[src[:-1, :], src[1:, :]] += 1

    def forward(self, src: Tensor, mask: Tensor) -> Tensor:
        if not self._is_training:
            return self.infer(src)
        result = self.infer(src)
        self.count(src)
        return result

    def __call__(self, *args, **kwargs):
        return self.forward(*args, **kwargs)


class PositionalEncoding(nn.Module):

    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        position = torch.arange(max_len).unsqueeze(1)
        # { 1/10000 } ^ { d/d_model }
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
        pe = torch.zeros(max_len, 1, d_model)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x: Tensor) -> Tensor:
        """
        Args:
            x: Tensor, shape [seq_len, batch_size, embedding_dim]
        """
        x = x + self.pe[:x.size(0)]
        return self.dropout(x)


class TransformerModel(nn.Module):
    def __init__(self, ntoken: int, d_model: int, nhead: int, d_hid: int,
                 nlayers: int, dropout: float = 0.5):
        super().__init__()
        self.model_type = 'Transformer'
        self.pos_encoder = PositionalEncoding(d_model, dropout)
        encoder_layers = TransformerEncoderLayer(d_model, nhead, d_hid, dropout)
        self.transformer_encoder = TransformerEncoder(encoder_layers, nlayers)
        self.encoder = nn.Embedding(ntoken, d_model)
        self.d_model = d_model
        self.decoder = nn.Linear(d_model, ntoken)

        self.init_weights()

    def init_weights(self) -> None:
        initrange = 0.1
        self.encoder.weight.data.uniform_(-initrange, initrange)
        self.decoder.bias.data.zero_()
        self.decoder.weight.data.uniform_(-initrange, initrange)

    def forward(self, src: Tensor, src_mask: Tensor) -> Tensor:
        """
        Args:
            src: Tensor, shape [seq_len, batch_size]
            src_mask: Tensor, shape [seq_len, seq_len]

        Returns:
            output Tensor of shape [seq_len, batch_size, ntoken]
        """
        src = self.encoder(src) * math.sqrt(self.d_model)
        src = self.pos_encoder(src)
        output = self.transformer_encoder(src, src_mask)
        output = self.decoder(output)
        return output


def generate_square_subsequent_mask(sz: int) -> Tensor:
    """Generates an upper-triangular matrix of -inf, with zeros on diag."""
    return torch.triu(torch.ones(sz, sz) * float('-inf'), diagonal=1)


def get_batch(source: Tensor, i: int) -> Tuple[Tensor, Tensor]:
    """
    Args:
        source: Tensor, shape [full_seq_len, batch_size]
        i: int

    Returns:
        tuple (data, target), where data has shape [seq_len, batch_size] and
        target has shape [seq_len * batch_size]
    """
    seq_len = min(bptt, len(source) - 1 - i)
    data = source[i:i+seq_len]
    target = source[i+1:i+1+seq_len].reshape(-1)
    return data, target


def data_process(raw_text_iter: dataset.IterableDataset, tokenizer, vocab) -> Tensor:
    """Converts raw text into a flat Tensor."""
    data = [torch.tensor(vocab(tokenizer(item)), dtype=torch.long) for item in raw_text_iter]
    return torch.cat(tuple(filter(lambda t: t.numel() > 0, data)))

def batchify(data: Tensor, bsz: int) -> Tensor:
    """Divides the data into bsz separate sequences, removing extra elements
    that wouldn't cleanly fit.

    Args:
        data: Tensor, shape [N]
        bsz: int, batch size

    Returns:
        Tensor of shape [N // bsz, bsz]
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    seq_len = data.size(0) // bsz
    data = data[:seq_len * bsz]
    data = data.view(bsz, seq_len).t().contiguous()
    return data.to(device)

def prepare_data_simple():
    train_iter = datasets.PhoneNumberDigits()
    tokenizer = list
    vocab = build_vocab_from_iterator(map(tokenizer, train_iter), specials=['#'])
    vocab.set_default_index(vocab['#'])

    train_iter = datasets.PhoneNumberDigits()
    train_data = data_process(train_iter, tokenizer, vocab)

    train_data = batchify(train_data, 4)  # shape [seq_len, batch_size]
    return vocab, train_data, train_data, train_data

def prepare_data():
    train_iter = WikiText2(split='train')
    tokenizer = get_tokenizer('basic_english')
    vocab = build_vocab_from_iterator(map(tokenizer, train_iter), specials=['<unk>'])
    vocab.set_default_index(vocab['<unk>'])

    # train_iter was "consumed" by the process of building the vocab,
    # so we have to create it again
    train_iter, val_iter, test_iter = WikiText2()
    train_data = data_process(train_iter, tokenizer, vocab)
    val_data = data_process(val_iter, tokenizer, vocab)
    test_data = data_process(test_iter, tokenizer, vocab)

    batch_size = 20
    eval_batch_size = 10
    train_data = batchify(train_data, batch_size)  # shape [seq_len, batch_size]
    val_data = batchify(val_data, eval_batch_size)
    test_data = batchify(test_data, eval_batch_size)
    return vocab, train_data, val_data, test_data


def run_models(vocab, train_data, val_data, test_data):
    ntokens = len(vocab)  # size of vocabulary
    emsize = 200  # embedding dimension
    d_hid = 200  # dimension of the feedforward network model in nn.TransformerEncoder
    nlayers = 2  # number of nn.TransformerEncoderLayer in nn.TransformerEncoder
    nhead = 2  # number of heads in nn.MultiheadAttention
    dropout = 0.2  # dropout probability
    model = TransformerModel(ntokens, emsize, nhead, d_hid, nlayers, dropout).to(device)

    criterion = nn.CrossEntropyLoss()
    lr = 5.0  # learning rate
    optimizer = torch.optim.SGD(model.parameters(), lr=lr)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, 1.0, gamma=0.95)

    def train(model: nn.Module, epoch: int) -> None:
        model.train()  # turn on train mode
        total_loss = 0.
        log_interval = 200
        start_time = time.time()
        src_mask = generate_square_subsequent_mask(bptt).to(device)

        num_batches = len(train_data) // bptt
        for batch, i in enumerate(range(0, train_data.size(0) - 1, bptt)):
            data, targets = get_batch(train_data, i)
            batch_size = data.size(0)
            if batch_size != bptt:  # only on last batch
                src_mask = src_mask[:batch_size, :batch_size]
            output = model(data, src_mask)
            # 不同的表现形式
            loss = criterion(output.view(-1, ntokens), targets)

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 0.5)
            optimizer.step()

            total_loss += loss.item()
            if batch % log_interval == 0 and batch > 0:
                lr = scheduler.get_last_lr()[0]
                ms_per_batch = (time.time() - start_time) * 1000 / log_interval
                cur_loss = total_loss / log_interval
                ppl = math.exp(cur_loss)
                print(f'| epoch {epoch:3d} | {batch:5d}/{num_batches:5d} batches | '
                      f'lr {lr:02.2f} | ms/batch {ms_per_batch:5.2f} | '
                      f'loss {cur_loss:5.2f} | ppl {ppl:8.2f}')
                total_loss = 0
                start_time = time.time()

    def evaluate(model: nn.Module, eval_data: Tensor) -> float:
        model.eval()  # turn on evaluation mode
        total_loss = 0.
        src_mask = generate_square_subsequent_mask(bptt).to(device)
        with torch.no_grad():
            for i in range(0, eval_data.size(0) - 1, bptt):
                data, targets = get_batch(eval_data, i)
                batch_size = data.size(0)
                if batch_size != bptt:
                    src_mask = src_mask[:batch_size, :batch_size]
                output = model(data, src_mask)
                output_flat = output.view(-1, ntokens)
                total_loss += batch_size * criterion(output_flat, targets).item()
        return total_loss / (len(eval_data) - 1)

    best_val_loss = float('inf')
    epochs = 3
    best_model = None
    for epoch in range(1, epochs + 1):
        epoch_start_time = time.time()
        train(model, epoch)
        val_loss = evaluate(model, val_data)
        val_ppl = math.exp(val_loss)
        elapsed = time.time() - epoch_start_time
        print('-' * 89)
        print(f'| end of epoch {epoch:3d} | time: {elapsed:5.2f}s | '
              f'valid loss {val_loss:5.2f} | valid ppl {val_ppl:8.2f}')
        print('-' * 89)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_model = copy.deepcopy(model)

        scheduler.step()
    return best_model

def run_baseline_models(vocab, train_data, val_data, test_data):
    ntokens = len(vocab)  # size of vocabulary
    model = BigramModel(ntokens)

    criterion = nn.CrossEntropyLoss()

    def train(model: nn.Module, epoch: int) -> None:
        model.train()  # turn on train mode
        total_loss = 0.
        log_interval = 200
        start_time = time.time()
        src_mask = generate_square_subsequent_mask(bptt).to(device)

        num_batches = len(train_data) // bptt
        for batch, i in enumerate(range(0, train_data.size(0) - 1, bptt)):
            data, targets = get_batch(train_data, i)
            batch_size = data.size(0)
            if batch_size != bptt:  # only on last batch
                src_mask = src_mask[:batch_size, :batch_size]
            output = model(data, src_mask)
            # 不同的表现形式
            loss = criterion(output.view(-1, ntokens), targets)

            total_loss += loss.item()
            if batch % log_interval == 0 and batch > 0:
                ms_per_batch = (time.time() - start_time) * 1000 / log_interval
                cur_loss = total_loss / log_interval
                ppl = math.exp(cur_loss)
                print(f'| epoch {epoch:3d} | {batch:5d}/{num_batches:5d} batches | '
                      f'lr {0:02.2f} | ms/batch {ms_per_batch:5.2f} | '
                      f'loss {cur_loss:5.2f} | ppl {ppl:8.2f}')
                total_loss = 0
                start_time = time.time()

    def evaluate(model: nn.Module, eval_data: Tensor) -> float:
        model.eval()  # turn on evaluation mode
        total_loss = 0.
        src_mask = generate_square_subsequent_mask(bptt).to(device)
        with torch.no_grad():
            for i in range(0, eval_data.size(0) - 1, bptt):
                data, targets = get_batch(eval_data, i)
                batch_size = data.size(0)
                if batch_size != bptt:
                    src_mask = src_mask[:batch_size, :batch_size]
                output = model(data, src_mask)
                output_flat = output.view(-1, ntokens)
                total_loss += batch_size * criterion(output_flat, targets).item()
        return total_loss / (len(eval_data) - 1)

    best_val_loss = float('inf')
    epochs = 1
    best_model = None
    for epoch in range(1, epochs + 1):
        epoch_start_time = time.time()
        train(model, epoch)
        val_loss = evaluate(model, val_data)
        val_ppl = math.exp(val_loss)
        elapsed = time.time() - epoch_start_time
        print('-' * 89)
        print(f'| end of epoch {epoch:3d} | time: {elapsed:5.2f}s | '
              f'valid loss {val_loss:5.2f} | valid ppl {val_ppl:8.2f}')
        print('-' * 89)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_model = copy.deepcopy(model)

    return best_model
if __name__ == "__main__":
    vocab, train_data, val_data, test_data = prepare_data_simple()
    run_models(vocab, train_data, val_data, test_data)
    # run_baseline_models(ntokens, train_data, val_data, test_data)
