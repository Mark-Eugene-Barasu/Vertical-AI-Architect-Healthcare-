import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, ScrollView, StyleSheet, Alert } from "react-native";
import { Audio } from "expo-av";
import { mobileApi } from "../services/api";

export default function NoteScreen() {
  const [patientId, setPatientId] = useState("");
  const [transcript, setTranscript] = useState("");
  const [note, setNote] = useState<any>(null);
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [loading, setLoading] = useState(false);

  const startRecording = async () => {
    await Audio.requestPermissionsAsync();
    await Audio.setAudioModeAsync({ allowsRecordingIOS: true, playsInSilentModeIOS: true });
    const { recording } = await Audio.Recording.createAsync(Audio.RecordingOptionsPresets.HIGH_QUALITY);
    setRecording(recording);
  };

  const stopRecording = async () => {
    if (!recording) return;
    await recording.stopAndUnloadAsync();
    const uri = recording.getURI();
    setRecording(null);
    setTranscript(`[Audio recorded: ${uri}]\nTranscript will appear after processing...`);
  };

  const generateNote = async () => {
    if (!transcript || !patientId) return Alert.alert("Missing fields", "Patient ID and transcript required");
    setLoading(true);
    try {
      const { data } = await mobileApi.generateNote(transcript, patientId);
      setNote(data.clinical_note);
    } catch {
      Alert.alert("Error", "Failed to generate note");
    } finally {
      setLoading(false);
    }
  };

  const SOAP_KEYS = ["subjective", "objective", "assessment", "plan", "follow_up"] as const;

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>🎙️ Clinical Notes</Text>
      <TextInput style={styles.input} placeholder="Patient ID" value={patientId} onChangeText={setPatientId} />

      <View style={styles.recordRow}>
        <TouchableOpacity style={[styles.recordBtn, recording ? styles.recording : {}]} onPress={recording ? stopRecording : startRecording}>
          <Text style={styles.recordBtnText}>{recording ? "⏹ Stop Recording" : "🎙️ Record"}</Text>
        </TouchableOpacity>
      </View>

      <TextInput style={[styles.input, styles.textarea]} placeholder="Or paste transcript here..."
        value={transcript} onChangeText={setTranscript} multiline numberOfLines={6} />

      <TouchableOpacity style={[styles.btn, loading && styles.btnDisabled]} onPress={generateNote} disabled={loading}>
        <Text style={styles.btnText}>{loading ? "Generating..." : "Generate SOAP Note"}</Text>
      </TouchableOpacity>

      {note && (
        <View style={styles.noteCard}>
          <Text style={styles.noteTitle}>Generated SOAP Note</Text>
          {SOAP_KEYS.map((key) => (
            <View key={key} style={styles.soapSection}>
              <Text style={styles.soapKey}>{key.replace("_", " ").toUpperCase()}</Text>
              <Text style={styles.soapValue}>{note[key]}</Text>
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container:    { flex: 1, backgroundColor: "#f0f4f8" },
  content:      { padding: 16 },
  title:        { fontSize: 20, fontWeight: "bold", marginBottom: 16, color: "#1a365d" },
  input:        { backgroundColor: "#fff", borderRadius: 10, padding: 12, marginBottom: 12, fontSize: 15, borderWidth: 1, borderColor: "#e2e8f0" },
  textarea:     { height: 120, textAlignVertical: "top" },
  recordRow:    { marginBottom: 12 },
  recordBtn:    { backgroundColor: "#2b6cb0", borderRadius: 10, padding: 14, alignItems: "center" },
  recording:    { backgroundColor: "#e53e3e" },
  recordBtnText:{ color: "#fff", fontWeight: "bold" },
  btn:          { backgroundColor: "#2b6cb0", borderRadius: 10, padding: 14, alignItems: "center", marginBottom: 16 },
  btnDisabled:  { opacity: 0.6 },
  btnText:      { color: "#fff", fontWeight: "bold", fontSize: 15 },
  noteCard:     { backgroundColor: "#fff", borderRadius: 10, padding: 16, borderWidth: 1, borderColor: "#e2e8f0" },
  noteTitle:    { fontWeight: "bold", fontSize: 16, marginBottom: 12, color: "#1a365d" },
  soapSection:  { marginBottom: 10 },
  soapKey:      { fontSize: 11, color: "#718096", fontWeight: "bold", letterSpacing: 0.5 },
  soapValue:    { fontSize: 14, color: "#2d3748", marginTop: 2 },
});
