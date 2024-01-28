import { createContext, useState } from "react";

export const DataContext = createContext(null);

export default function DataProvider({ children }) {
  const [customCharacteristic, setCustomCharacteristic] = useState(null);

  return (
    <DataContext.Provider
      value={{
        customCharacteristic,
        setCustomCharacteristic,
      }}
    >
      {children}
    </DataContext.Provider>
  );
}
