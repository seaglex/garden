import torch
from torch import Tensor
import torch.nn.functional as F
from torch.nn.modules.activation import MultiheadAttention
from nlp.my_multihead_attention import MyMultiHeadAttention
from torch.nn.modules.transformer import TransformerEncoderLayer

'''
            return F.multi_head_attention_forward(
                query, key, value, self.embed_dim, self.num_heads,
                self.in_proj_weight, self.in_proj_bias,
                self.bias_k, self.bias_v, self.add_zero_attn,
                self.dropout, self.out_proj.weight, self.out_proj.bias,
                training=self.training,
                key_padding_mask=key_padding_mask, need_weights=need_weights,
                attn_mask=attn_mask)
'''
def test_library():
    d_model = 4
    n_heads = 2
    n_batch = 1
    n_targets = 2
    n_sources = 3
    queries = torch.zeros(n_targets, n_batch, d_model)  # L, N, E
    for n in range(n_targets):
        for d in range(d_model):
            queries[n, 0, d] = n if d == n else 0
    keys = torch.zeros(n_sources, n_batch, d_model)  # S, N, E
    for n in range(n_sources):
        for d in range(d_model):
            keys[n, 0, d] = n if d == n else 0
    values = keys
    in_proj_weights = torch.randn(3 * d_model, d_model)
    in_proj_bias = torch.randn(3 * d_model)
    attention = MultiheadAttention(d_model, n_heads)
    results = attention.forward(queries, keys, values)
    print(results)


def compare_libraries():
    d_model = 4
    n_heads = 2
    n_batch = 1
    S = 3
    std_lib = MultiheadAttention(d_model, n_heads)
    my_lib = MyMultiHeadAttention(d_model, n_heads)
    my_lib.in_proj_weight = std_lib.in_proj_weight
    my_lib.in_proj_bias = std_lib.in_proj_bias
    my_lib.out_proj_weight = std_lib.out_proj.weight
    my_lib.out_proj_bias = std_lib.out_proj.bias

    x = torch.randn(S, n_batch, d_model)
    attention_mask = (torch.ones(S, S) * float("-inf")).triu(diagonal=1)
    std_out = std_lib.forward(x, x, x, attn_mask=attention_mask)[0]
    my_out = my_lib.self_attention_forward(x, attention_mask)
    print("diff", (std_out - my_out).abs().sum())

if __name__ == "__main__":
    test_library()
