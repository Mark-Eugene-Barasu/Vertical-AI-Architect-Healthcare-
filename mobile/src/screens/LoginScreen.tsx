import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert } from "react-native";
import { signIn } from "aws-amplify/auth";

export default function LoginScreen({ navigation }: any) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    try {
      await signIn({ username: email, password });
      navigation.replace("Main");
    } catch (e: any) {
      Alert.alert("Login Failed", e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.logo}>🧠 MediMind AI</Text>
      <Text style={styles.subtitle}>Clinical Co-Pilot</Text>
      <TextInput style={styles.input} placeholder="Email" value={email}
        onChangeText={setEmail} keyboardType="email-address" autoCapitalize="none" />
      <TextInput style={styles.input} placeholder="Password" value={password}
        onChangeText={setPassword} secureTextEntry />
      <TouchableOpacity style={[styles.btn, loading && styles.btnDisabled]} onPress={handleLogin} disabled={loading}>
        <Text style={styles.btnText}>{loading ? "Signing in..." : "Sign In"}</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", padding: 24, backgroundColor: "#1a365d" },
  logo:      { fontSize: 32, fontWeight: "bold", color: "#fff", textAlign: "center", marginBottom: 8 },
  subtitle:  { fontSize: 16, color: "#90cdf4", textAlign: "center", marginBottom: 40 },
  input:     { backgroundColor: "#fff", borderRadius: 10, padding: 14, marginBottom: 16, fontSize: 16 },
  btn:       { backgroundColor: "#2b6cb0", borderRadius: 10, padding: 16, alignItems: "center" },
  btnDisabled: { opacity: 0.6 },
  btnText:   { color: "#fff", fontWeight: "bold", fontSize: 16 },
});
