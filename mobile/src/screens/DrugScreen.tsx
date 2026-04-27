import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, ScrollView, StyleSheet, Alert } from "react-native";
import { mobileApi } from "../services/api";

export default function DrugScreen() {
  const [patientId, setPatientId] = useState("");
  const [text, setText] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const checkDrugs = async () => {
    if (!text) return Alert.alert("Missing input", "Enter medications or clinical text");
    setLoading(true);
    try {
      const { data } = await mobileApi.checkDrugs(text, patientId);
      setResult(data);
    } catch {
      Alert.alert("Error", "Failed to check interactions");
    } finally {
      setLoading(false);
    }
  };

  const severityColor = (s: string) => s === "HIGH" ? "#e53e3e" : s === "MEDIUM" ? "#dd6b20" : "#38a169";

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>💊 Drug Interactions</Text>
      <TextInput style={styles.input} placeholder="Patient ID (optional)" value={patientId} onChangeText={setPatientId} />
      <TextInput style={[styles.input, styles.textarea]} placeholder="Enter medications or clinical text..."
        value={text} onChangeText={setText} multiline numberOfLines={5} />
      <TouchableOpacity style={[styles.btn, loading && styles.btnDisabled]} onPress={checkDrugs} disabled={loading}>
        <Text style={styles.btnText}>{loading ? "Checking..." : "Check Interactions"}</Text>
      </TouchableOpacity>

      {result && (
        <>
          <Text style={styles.sectionTitle}>Detected Medications</Text>
          <View style={styles.tagRow}>
            {result.medications.map((m: string) => (
              <View key={m} style={styles.tag}><Text style={styles.tagText}>{m}</Text></View>
            ))}
          </View>

          <Text style={styles.sectionTitle}>
            Interactions {result.interactions.length === 0 ? "— None Found ✅" : ""}
          </Text>
          {result.interactions.map((i: any, idx: number) => (
            <View key={idx} style={[styles.interactionCard, { borderLeftColor: severityColor(i.severity) }]}>
              <Text style={[styles.severity, { color: severityColor(i.severity) }]}>{i.severity} RISK</Text>
              <Text style={styles.warning}>{i.warning}</Text>
            </View>
          ))}
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container:       { flex: 1, backgroundColor: "#f0f4f8" },
  content:         { padding: 16 },
  title:           { fontSize: 20, fontWeight: "bold", marginBottom: 16, color: "#1a365d" },
  input:           { backgroundColor: "#fff", borderRadius: 10, padding: 12, marginBottom: 12, fontSize: 15, borderWidth: 1, borderColor: "#e2e8f0" },
  textarea:        { height: 100, textAlignVertical: "top" },
  btn:             { backgroundColor: "#2b6cb0", borderRadius: 10, padding: 14, alignItems: "center", marginBottom: 16 },
  btnDisabled:     { opacity: 0.6 },
  btnText:         { color: "#fff", fontWeight: "bold", fontSize: 15 },
  sectionTitle:    { fontWeight: "bold", fontSize: 15, marginBottom: 8, color: "#2d3748" },
  tagRow:          { flexDirection: "row", flexWrap: "wrap", gap: 8, marginBottom: 16 },
  tag:             { backgroundColor: "#ebf8ff", borderRadius: 20, paddingHorizontal: 12, paddingVertical: 4 },
  tagText:         { color: "#2b6cb0", fontSize: 13 },
  interactionCard: { backgroundColor: "#fff5f5", borderRadius: 8, padding: 12, marginBottom: 8, borderLeftWidth: 4 },
  severity:        { fontWeight: "bold", marginBottom: 4 },
  warning:         { fontSize: 14, color: "#2d3748" },
});
