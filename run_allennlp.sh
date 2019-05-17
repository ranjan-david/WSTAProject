#!/bin/bash


MODEL=output/model.tar.gz
TEST_JSON=test.json


allennlp train decomposable_attention.json -s output
allennlp predict $MODEL $TEST_JSON --output-file da_predictions.json 

