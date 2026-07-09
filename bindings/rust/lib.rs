//! Mnestra memory interface — Rust binding (trait mirrors spec/mnestra.idl).
//! A substrate driver implements `Memory`; application code is substrate-agnostic.

pub type Address = String;

#[derive(Clone, Debug, Default)]
pub struct Pattern { pub text: String, pub summary: String, pub value: Vec<u8> }

#[derive(Clone, Debug)]
pub struct Recall { pub address: Address, pub score: f32 }

#[derive(Clone, Debug, Default)]
pub struct GlobalView {
    pub title: String,
    pub outline: Vec<String>,
    pub constraints: Vec<String>,
    pub recalled: Vec<Recall>,
    pub filled: usize,
    pub total: usize,
}

pub enum Substrate { Classical, Photonic, QuantumAfc }

/// One physical substrate behind the logical model.
pub trait Memory {
    fn write(&mut self, addr: &str, p: Pattern) -> Address;
    fn read(&self, addr: &str) -> Option<Pattern>;
    fn query(&self, cue: &str, k: usize) -> Vec<Recall>;
    fn reconstruct(&self) -> GlobalView;
}

/// Stable content address: BLAKE2b-128 of canonical-encoded payload (see ACF spec).
pub fn content_address(_payload: &str) -> Address { /* impl in driver crate */ String::new() }

pub fn open(_s: Substrate) -> Box<dyn Memory> { unimplemented!("provided by a substrate driver") }
