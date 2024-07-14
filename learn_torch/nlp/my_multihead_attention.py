import torch
from torch import nn, Tensor
import torch.nn.functional as F
import math


class MyMultiHeadAttention(nn.Module):
    def __init__(self, d_model: int, n_heads: int):
        super().__init__()
        self.model_type = 'MyMultiHeadAttention'
        self._d_model = d_model
        self._n_heads = n_heads
        assert d_model % n_heads == 0, "d_model / n_head  = {0} / {1}".format(d_model, n_heads)
        self.in_proj_weight = torch.empty(d_model * 3, d_model)
        self.in_proj_bias = torch.empty(d_model * 3)
        self.out_proj_weight = torch.empty(d_model, d_model)
        self.out_proj_weight = torch.empty(d_model)

    def self_attention_forward(self,
        x: Tensor, attention_mask: Tensor
    ) -> Tensor:
        '''
        :param x: [source_len, batch_sz, d_model]
        :param attention_mask:[target_len, source_len]
        :return: [target_len, batch_sz, d_model]
        '''
        in_proj = F.linear(x, self.in_proj_weight, self.in_proj_bias)
        in_proj = in_proj.transpose(0, -2)  # [batch_sz, source_len, d_model]
        q, k, v = in_proj.chunk(3, dim=-1)
        q = q.unflatten(-1, (self._n_heads, -1)).transpose(-2, -3)  # [batch_sz, n_heads, source_len, d_model / n_head]
        k = k.unflatten(-1, (self._n_heads, -1)).transpose(-2, -3)
        v = v.unflatten(-1, (self._n_heads, -1)).transpose(-2, -3)  # [batch_sz, n_heads, target_len, d_model / n_head]
        attentions = q @ k.transpose(-1, -2) / math.sqrt(self._d_model / self._n_heads)  # [batch_sz, n_heads, target_len, source_len]
        attentions += attention_mask
        attentions = F.softmax(attentions, dim=-1)
        out = attentions @ v
        out = out.transpose(-2, -3).flatten(-2, -1).transpose(0, -2)
        out = F.linear(out, self.out_proj_weight, self.out_proj_bias)
        return out
