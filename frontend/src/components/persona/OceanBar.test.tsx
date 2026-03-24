import React from "react";
import { render, screen } from "@testing-library/react";
import { OceanBar } from "./OceanBar";

const mockScores = {
  openness: 0.75,
  conscientiousness: 0.60,
  extraversion: 0.40,
  agreeableness: 0.85,
  neuroticism: 0.30,
};

describe("OceanBar", () => {
  it("renders all 5 trait labels", () => {
    render(<OceanBar scores={mockScores} />);
    expect(screen.getByText("Openness")).toBeInTheDocument();
    expect(screen.getByText("Conscientiousness")).toBeInTheDocument();
    expect(screen.getByText("Extraversion")).toBeInTheDocument();
    expect(screen.getByText("Agreeableness")).toBeInTheDocument();
    expect(screen.getByText("Neuroticism")).toBeInTheDocument();
  });

  it("renders score percentages as text", () => {
    render(<OceanBar scores={mockScores} />);
    expect(screen.getByText("75%")).toBeInTheDocument();
    expect(screen.getByText("60%")).toBeInTheDocument();
    expect(screen.getByText("40%")).toBeInTheDocument();
    expect(screen.getByText("85%")).toBeInTheDocument();
    expect(screen.getByText("30%")).toBeInTheDocument();
  });

  it("renders 5 bar elements", () => {
    render(<OceanBar scores={mockScores} />);
    const bars = screen.getAllByRole("progressbar");
    expect(bars).toHaveLength(5);
  });

  it("sets correct width on progress bars", () => {
    render(<OceanBar scores={mockScores} />);
    const bars = screen.getAllByRole("progressbar");
    // openness is 0.75 → 75%
    expect(bars[0]).toHaveStyle({ width: "75%" });
  });

  it("handles edge values: 0 and 1", () => {
    render(
      <OceanBar
        scores={{
          openness: 0,
          conscientiousness: 1,
          extraversion: 0.5,
          agreeableness: 0.5,
          neuroticism: 0.5,
        }}
      />
    );
    expect(screen.getByText("0%")).toBeInTheDocument();
    expect(screen.getByText("100%")).toBeInTheDocument();
  });
});
