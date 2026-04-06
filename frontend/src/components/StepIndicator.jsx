import React from "react";
import "./StepIndicator.css";

const STEPS = [
  { num: 1, label: "Chon bai hat" },
  { num: 2, label: "Bo loc" },
  { num: 3, label: "Ket qua" },
];

function StepIndicator({ currentStep, onStepClick }) {
  return (
    <div className="step-indicator">
      {STEPS.map((s) => (
        <div
          key={s.num}
          className={`step-indicator__item ${
            currentStep >= s.num ? "step-indicator__item--active" : ""
          }`}
          onClick={() => s.num < currentStep && onStepClick(s.num)}
        >
          <div className="step-indicator__circle">{s.num}</div>
          <span className="step-indicator__label">{s.label}</span>
        </div>
      ))}
    </div>
  );
}

export default StepIndicator;
