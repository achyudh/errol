import torch
import torch.nn as nn

from models.sm_cnn.encoder import KimCNNEncoder


class SiameseCNN(nn.Module):
    def __init__(self, args):
        super().__init__()

        if args.mode == 'rand':
            query_embed_init = torch.Tensor(args.query_vocab_len, args.embed_dim).uniform_(-0.25, 0.25)
            self.query_embed = nn.Embedding.from_pretrained(query_embed_init, freeze=False)
            input_embed_init = torch.Tensor(args.input_vocab_len, args.embed_dim).uniform_(-0.25, 0.25)
            self.input_embed = nn.Embedding.from_pretrained(input_embed_init, freeze=False)
        else:
            is_frozen = (args.mode == 'static')
            self.query_embed = nn.Embedding.from_pretrained(args.dataset.fields['query'].vocab.vectors, is_frozen)
            self.input_embed = nn.Embedding.from_pretrained(args.dataset.fields['input'].vocab.vectors, is_frozen)

        self.encoder = KimCNNEncoder(args)
        self.fc1 = nn.Linear(6 * args.output_channel, args.target_class)

    def forward(self, query, input, **kwargs):
        query = self.query_embed(query).unsqueeze(1)  # (batch, channel_input, sent_len, embed_dim)
        input = self.input_embed(input).unsqueeze(1)  # (batch, channel_input, sent_len, embed_dim)

        query = self.encoder(query)  # (batch, channel_output * num_conv)
        input = self.encoder(input)  # (batch, channel_output * num_conv)
        x = torch.cat([query, input], 1)   # (batch, 2 * channel_output * num_conv)
        return self.fc1(x)  # (batch, target_size)
