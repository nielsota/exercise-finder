"""
Tests for paths.py: verify directory structure and file naming conventions.
"""

import re # type: ignore[import-untyped]

import pytest # type: ignore[import-not-found]

from exercise_finder import paths # type: ignore[import-not-found]


class TestDirectoryExistence:
    """Test that key directories exist."""

    def test_repo_root_exists(self):
        """Repo root should exist."""
        assert paths.repo_root().exists()
        assert paths.repo_root().is_dir()

    def test_data_dir_exists(self):
        """Data directory should exist."""
        assert paths.data_dir().exists()
        assert paths.data_dir().is_dir()

    def test_questions_images_root_exists(self):
        """Questions images root should exist."""
        assert paths.questions_images_root().exists()
        assert paths.questions_images_root().is_dir()

    def test_questions_extracted_dir_exists(self):
        """Questions extracted directory should exist."""
        assert paths.questions_extracted_dir().exists()
        assert paths.questions_extracted_dir().is_dir()

    def test_questions_formatted_dir_exists(self):
        """Questions formatted directory should exist."""
        assert paths.questions_formatted_dir().exists()
        assert paths.questions_formatted_dir().is_dir()

    def test_practice_exercises_dir_exists(self):
        """Practice exercises directory should exist."""
        assert paths.practice_exercises_dir().exists()
        assert paths.practice_exercises_dir().is_dir()

    def test_vectorstore_index_dir_exists(self):
        """Vectorstore index directory should exist."""
        assert paths.vectorstore_index_dir().exists()
        assert paths.vectorstore_index_dir().is_dir()


class TestQuestionsExtractedStructure:
    """
    Test the structure of data/questions-extracted/.
    
    Expected structure:
        data/questions-extracted/
            <exam-id>/
                q1.yaml
                q2.yaml
                ...
    """

    def test_extracted_contains_exam_dirs(self):
        """Questions extracted should contain exam directories."""
        extracted_dir = paths.questions_extracted_dir()
        
        # Get all subdirectories (should be exam IDs)
        exam_dirs = [d for d in extracted_dir.iterdir() if d.is_dir()]
        
        # Should have at least one exam
        assert len(exam_dirs) > 0, "No exam directories found in questions-extracted"

    def test_extracted_exam_dirs_contain_yaml_files(self):
        """Each exam directory should contain YAML files."""
        extracted_dir = paths.questions_extracted_dir()
        exam_dirs = [d for d in extracted_dir.iterdir() if d.is_dir()]
        
        for exam_dir in exam_dirs:
            yaml_files = list(exam_dir.glob("*.yaml"))
            assert len(yaml_files) > 0, f"No YAML files found in {exam_dir.name}"

    def test_extracted_yaml_files_follow_naming_convention(self):
        """
        YAML files in extracted directories should follow q<N>.yaml pattern.
        
        Examples: q1.yaml, q2.yaml, q03.yaml, q10.yaml
        """
        extracted_dir = paths.questions_extracted_dir()
        exam_dirs = [d for d in extracted_dir.iterdir() if d.is_dir()]
        
        # Pattern: q followed by digits, .yaml extension
        pattern = re.compile(r"^q\d+\.yaml$")
        
        for exam_dir in exam_dirs:
            yaml_files = list(exam_dir.glob("*.yaml"))
            
            for yaml_file in yaml_files:
                assert pattern.match(yaml_file.name), (
                    f"File {yaml_file.name} in {exam_dir.name} does not match "
                    f"pattern q<N>.yaml"
                )


class TestQuestionsFormattedStructure:
    """
    Test the structure of data/questions-formatted/.
    
    Expected structure:
        data/questions-formatted/
            exams/
                <exam-id>/
                    q1.yaml
                    q2.yaml
                    ...
            practice-exercises/
                <topic>/
                    _meta.yaml
                    p1.yaml
                    p2.yaml
                    ...
    """

    def test_formatted_contains_exams_subdir(self):
        """Questions formatted should contain 'exams' subdirectory."""
        formatted_dir = paths.questions_formatted_dir()
        exams_dir = formatted_dir / "exams"
        
        assert exams_dir.exists(), "exams/ subdirectory not found in questions-formatted"
        assert exams_dir.is_dir()

    def test_formatted_exams_contain_yaml_files(self):
        """Each formatted exam directory should contain YAML files."""
        formatted_dir = paths.questions_formatted_dir()
        exams_dir = formatted_dir / "exams"
        
        if not exams_dir.exists():
            pytest.skip("exams/ directory not found")
        
        exam_dirs = [d for d in exams_dir.iterdir() if d.is_dir()]
        
        # Should have at least one exam
        if len(exam_dirs) == 0:
            pytest.skip("No formatted exam directories found")
        
        for exam_dir in exam_dirs:
            yaml_files = list(exam_dir.glob("*.yaml"))
            assert len(yaml_files) > 0, f"No YAML files found in {exam_dir.name}"

    def test_formatted_yaml_files_follow_naming_convention(self):
        """
        YAML files in formatted exam directories should follow q<N>.yaml pattern.
        
        Examples: q1.yaml, q2.yaml, q03.yaml, q10.yaml
        """
        formatted_dir = paths.questions_formatted_dir()
        exams_dir = formatted_dir / "exams"
        
        if not exams_dir.exists():
            pytest.skip("exams/ directory not found")
        
        exam_dirs = [d for d in exams_dir.iterdir() if d.is_dir()]
        
        if len(exam_dirs) == 0:
            pytest.skip("No formatted exam directories found")
        
        # Pattern: q followed by digits, .yaml extension
        pattern = re.compile(r"^q\d+\.yaml$")
        
        for exam_dir in exam_dirs:
            yaml_files = list(exam_dir.glob("*.yaml"))
            
            for yaml_file in yaml_files:
                assert pattern.match(yaml_file.name), (
                    f"File {yaml_file.name} in {exam_dir.name} does not match "
                    f"pattern q<N>.yaml"
                )


class TestPracticeExercisesStructure:
    """
    Test the structure of data/questions-formatted/practice-exercises/.
    
    Expected structure:
        data/questions-formatted/practice-exercises/
            <topic>/
                _meta.yaml
                p1.yaml
                p2.yaml
                ...
    """

    def test_practice_contains_topic_dirs(self):
        """Practice exercises should contain topic directories."""
        practice_dir = paths.practice_exercises_dir()
        
        # Get all subdirectories (should be topics)
        topic_dirs = [d for d in practice_dir.iterdir() if d.is_dir()]
        
        # Should have at least one topic
        assert len(topic_dirs) > 0, "No topic directories found in practice-exercises"

    def test_practice_topics_contain_meta_file(self):
        """Each topic directory should contain a _meta.yaml file."""
        practice_dir = paths.practice_exercises_dir()
        topic_dirs = [d for d in practice_dir.iterdir() if d.is_dir()]
        
        for topic_dir in topic_dirs:
            meta_file = topic_dir / "_meta.yaml"
            assert meta_file.exists(), f"Missing _meta.yaml in {topic_dir.name}"
            assert meta_file.is_file()

    def test_practice_topics_contain_exercise_files(self):
        """Each topic directory should contain p*.yaml exercise files."""
        practice_dir = paths.practice_exercises_dir()
        topic_dirs = [d for d in practice_dir.iterdir() if d.is_dir()]
        
        for topic_dir in topic_dirs:
            # Get all p*.yaml files
            exercise_files = list(topic_dir.glob("p*.yaml"))
            
            assert len(exercise_files) > 0, (
                f"No p*.yaml exercise files found in {topic_dir.name}"
            )

    def test_practice_yaml_files_follow_naming_convention(self):
        """
        YAML files in practice directories should follow p<N>.yaml pattern.
        
        Examples: p1.yaml, p2.yaml, p03.yaml, p10.yaml
        
        The _meta.yaml file is excluded from this check.
        """
        practice_dir = paths.practice_exercises_dir()
        topic_dirs = [d for d in practice_dir.iterdir() if d.is_dir()]
        
        # Pattern: p followed by digits, .yaml extension
        pattern = re.compile(r"^p\d+\.yaml$")
        
        for topic_dir in topic_dirs:
            yaml_files = list(topic_dir.glob("*.yaml"))
            
            for yaml_file in yaml_files:
                # Skip _meta.yaml
                if yaml_file.name == "_meta.yaml":
                    continue
                
                assert pattern.match(yaml_file.name), (
                    f"File {yaml_file.name} in {topic_dir.name} does not match "
                    f"pattern p<N>.yaml"
                )


class TestPathHelpers:
    """Test specific path helper functions."""

    def test_question_dirname_with_int(self):
        """question_dirname() should format integers as qNN."""
        assert paths.question_dirname(1) == "q01"
        assert paths.question_dirname(5) == "q05"
        assert paths.question_dirname(10) == "q10"
        assert paths.question_dirname(99) == "q99"

    def test_question_dirname_with_str(self):
        """question_dirname() should prepend 'q' to strings."""
        assert paths.question_dirname("1") == "q1"
        assert paths.question_dirname("05") == "q05"
        assert paths.question_dirname("10") == "q10"

    def test_practice_exercise_dir_builds_correct_path(self):
        """practice_exercise_dir() should build the correct path."""
        expected = paths.questions_formatted_dir() / "practice-exercises" / "unitcircle"
        actual = paths.practice_exercise_dir("unitcircle")
        
        assert actual == expected

    def test_formatted_exam_dir_builds_correct_path(self):
        """formatted_exam_dir() should build the correct path."""
        exam_id = "VW-1025-a-19-1-o"
        expected = paths.questions_formatted_dir() / "exams" / exam_id
        actual = paths.formatted_exam_dir(exam_id)
        
        assert actual == expected

    def test_formatted_question_path_builds_correct_path(self):
        """formatted_question_path() should build the correct path."""
        exam_id = "VW-1025-a-19-1-o"
        question_number = "1"
        expected = paths.questions_formatted_dir() / "exams" / exam_id / "q1.yaml"
        actual = paths.formatted_question_path(exam_id, question_number)
        
        assert actual == expected

