import React from "react";
import { FaSun, FaMoon } from "react-icons/fa";

const ToggleMode = ({ darkMode, toggleDarkMode }) => {
  return (
    <button onClick={toggleDarkMode} className="toggle-mode">
      {darkMode ? <FaMoon size={24} color="white" /> : <FaSun size={24} color="black" />}
    </button>
  );
};

export default ToggleMode;
