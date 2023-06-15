import torch


class Perplexity:
    def __call__(self, preds: torch.Tensor, labels: torch.Tensor):
        preds = preds.reshape((-1, preds.size(-1)))
        labels = labels.reshape((-1,))

        probs = preds[:, labels].diagonal()

        return torch.sum(-probs * torch.log(probs))
