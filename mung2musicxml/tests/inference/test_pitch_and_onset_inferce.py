# from unittest import TestCase, main
# from parameterized import parameterized

# from mung.constants import OnsetDataConstants
# from mung2musicxml.inference import OnsetInferenceEngineWrapper
# from mung2musicxml.tests.assets import ALL_EXAMPLES, AssetExample


# class RealExamplePitchOnsetInferenceTest(TestCase):
#     engine = OnsetInferenceEngineWrapper()
    
#     @parameterized.expand(
#         [
#             (type(sub).__name__, sub)
#             for sub in ALL_EXAMPLES
#         ]
#     )
#     def test_durations(self, name: str, example: AssetExample):
#         graph = example.get_graph()
#         self.engine(graph)
#         data = graph.collect_data(OnsetDataConstants.DURATION_BEATS)
#         self.assertDictEqual(example.expected_durations, data)

#     @parameterized.expand(
#         [
#             (type(sub).__name__, sub)
#             for sub in ALL_EXAMPLES
#         ]
#     )
#     def test_durations_without_modifiers(self, name: str, example: AssetExample):
#         graph = example.get_graph()
#         self.engine(graph)
#         data = graph.collect_data(OnsetDataConstants.DURATION_BEATS_WO_M)
#         self.assertDictEqual(example.expected_durations_without_modifiers, data)

#     @parameterized.expand(
#         [
#             (type(sub).__name__, sub)
#             for sub in ALL_EXAMPLES
#         ]
#     )
#     def test_onsets(self, name: str, example: AssetExample):
#         graph = example.get_graph()
#         self.engine(graph)
#         data = graph.collect_data(OnsetDataConstants.ONSET_BEATS)
#         self.assertDictEqual(example.expected_onsets, data)


# if __name__ == "__main__":
#     main()