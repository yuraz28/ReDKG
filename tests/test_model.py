import torch

torch.manual_seed(0)
import random

random.seed(0)
import numpy as np

np.random.seed(0)
import os

os.environ["CUDA_LAUNCH_BLOCKING"] = "1"

import sys

sys.path.append("../")

from redkg.kge import Evaluator, KGEModel
from redkg.kge_dataset import InfoData, KGEDataset

from tests.utils import read_test_data

train, test, valid = read_test_data()


def test_data_info():
    nentity, nrelation, v_tr, v_val, v_test, info = InfoData(train, test, valid).get_data()
    assert nentity == 20
    assert nrelation == 2
    assert v_tr == 71
    assert v_test == 14
    assert v_val == 14


def test_dataset():
    train_set = KGEDataset(train)
    test_set = KGEDataset(test, mode="tests")
    valid_set = KGEDataset(valid, mode="tests")

    assert len(train_set) == 100
    assert len(test_set) == 20
    assert len(valid_set) == 20

    train_set_first = (
        torch.cat([i.view(1) for i in train_set[0][0:3] + (train_set[0][5],)] + list(train_set[0][3:5]))
    ).tolist()
    test_set_first = (torch.cat([i.view(1) for i in test_set[0][0:3]] + list(test_set[0][3:]))).tolist()
    valid_set_first = (torch.cat([i.view(1) for i in valid_set[0][0:3]] + list(valid_set[0][3:]))).tolist()
    assert round(sum(train_set_first)) == 186
    assert round(sum(test_set_first)) == 210
    assert round(sum(valid_set_first)) == 221


def test_evaluator():
    evaluator = Evaluator()
    in_dict = {
        "y_pred_pos": torch.tensor([0.1]),
        "y_pred_neg": torch.tensor([[0.04, 0.11, 0.05, 0.03, 0.15, 0.07]]),
    }
    metrics = evaluator.eval(in_dict)
    assert round(sum(torch.cat(metrics).tolist()), 3) == 2.333


def test_model():
    evaluator = Evaluator()
    kge_model = KGEModel(model_name="TransE", nentity=20, nrelation=2, gamma=12, evaluator=evaluator)
    assert list(kge_model.entity_embedding.shape) == [20, 2]
    assert list(kge_model.relation_embedding.shape) == [2, 2]
    positive_score, negative_tail_score, negative_head_score = kge_model(
        torch.tensor(1), torch.tensor(11), torch.tensor(0), torch.tensor([[0, 2, 3]]), torch.tensor([[12, 13, 14]])
    )
    assert (
        round(
            sum(
                [
                    x
                    for l in positive_score.tolist() + negative_tail_score.tolist() + negative_head_score.tolist()
                    for x in l
                ]
            ),
            3,
        )
    ) == 10.778