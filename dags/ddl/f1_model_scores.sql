CREATE TABLE IF NOT EXISTS f1.model_accuracy_scores (
            fold_num NUMBER,
            r_squared FLOAT,
            accuracy_score FLOAT,
            ts VARCHAR(64)
        );