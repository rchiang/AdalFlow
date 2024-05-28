import pytest

from core.parameter import Parameter
from optim.optimizer import BootstrapFewShot
from optim.sampler import ClassSampler, RandomSampler


class TestBootstrapFewShotRandomSampler:

    def setup_method(self):
        self.num_shots = 10
        self.sampler = RandomSampler(
            dataset=self.mock_dataset(), default_num_shots=self.num_shots
        )
        self.optimizer = BootstrapFewShot(
            # parameter_dict={"test_examples_str": self.parameter},
            # parameter_name="test_examples_str",
            parameter=self.mock_parameter_obj(),
            sampler=self.sampler,
            output_processors=None,
            num_shots=self.num_shots,
        )

    def mock_dataset(self):
        self.num_classes = 10
        return [{"text": f"Sample text {i}", "label": i % 10} for i in range(100)]

    def get_key(self, item):
        return item["label"]

    def mock_parameter_obj(self):
        return Parameter("test_examples_str", "test_value")

    def test_initialization(self):
        assert self.optimizer.num_shots == self.num_shots
        assert self.optimizer.sampler == self.sampler

        # ensure assert fail when init is not called but random_replace is called
        with pytest.raises(AssertionError):
            self.optimizer.random_replace(2)
        # init the current examples
        self.optimizer.init()
        assert (
            len(self.optimizer.current) == self.num_shots
        ), f"Expected {self.num_shots} examples in current, got {len(self.optimizer.current)}"
        assert (
            len(self.optimizer.proposed) == self.num_shots
        ), f"Expected {self.num_shots} proposed examples"

    def test_propose(self):
        self.optimizer.init()

        examples = self.optimizer.propose(shots=5)
        print(f"examples: {examples}")

        assert len(examples) == 10, f"Expected 10 examples, got {len(examples)}"
        assert len(self.optimizer.proposed) == 10, f"Expected 10 proposed examples"
        # ensure there are 5 different examples in the current and proposed
        current_indexes = [item.index for item in self.optimizer.current]
        proposed_indexes = [item.index for item in self.optimizer.proposed]
        assert (
            len(set(current_indexes) & set(proposed_indexes)) == 5
        ), "Expected 5 common examples"

        # test that the example_parameter's data has the same value as the proposed examples
        for item_in_parameter, item in zip(
            self.optimizer.example_parameter.data, self.optimizer.proposed
        ):
            assert item_in_parameter.index == item.index, "Expected same index"
            assert item_in_parameter.data == item.data, "Expected same data"

    def test_reset_parameter(self):
        self.optimizer.init()
        self.optimizer.propose(shots=5)
        self.optimizer.reset_parameter()
        assert len(self.optimizer.proposed) == 0, "Expected proposed to be reset"
        assert (
            len(self.optimizer.current) == self.num_shots
        ), "Expected current to remain"
        # test that the example_parameter's data has the same value as the current examples
        for item_in_parameter, item in zip(
            self.optimizer.example_parameter.data, self.optimizer.current
        ):
            assert item_in_parameter.index == item.index, "Expected same index"
            assert item_in_parameter.data == item.data, "Expected same data"
