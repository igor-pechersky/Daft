use daft_dsl::ExprRef;
use serde::{Deserialize, Serialize};

use crate::PhysicalPlanRef;

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Filter {
    // Upstream node.
    pub input: PhysicalPlanRef,
    // The Boolean expression to filter on.
    pub predicate: ExprRef,
}

impl Filter {
    pub(crate) fn new(input: PhysicalPlanRef, predicate: ExprRef) -> Self {
        Self { input, predicate }
    }

    pub fn multiline_display(&self) -> Vec<String> {
        let mut res = vec![];
        res.push(format!("Filter: {}", self.predicate));
        res
    }
}
crate::impl_default_tree_display!(Filter);