import React, { useState } from 'react';
import { Button, TextInput, View, Text, Image, ScrollView } from 'react-native';
import * as ImagePicker from 'expo-image-picker';

const API_URL = 'http://192.168.1.100:8000'; // change to your backend IP

export default function App() {
  const [vin, setVin] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const decodeVin = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/decode-vin?vin=${vin}`);
      const data = await res.json();
      const mlRes = await fetch(`${API_URL}/predict-specs?vin=${vin}`);
      const mlData = await mlRes.json();
      setResult({ ...data, ...mlData });
    } catch (e) {
      alert('Error: ' + e.message);
    }
    setLoading(false);
  };

  const scanVin = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      alert('Camera permission required');
      return;
    }
    const result = await ImagePicker.launchCameraAsync({ base64: true });
    if (!result.canceled) {
      const formData = new FormData();
      formData.append('file', {
        uri: result.assets[0].uri,
        type: 'image/jpeg',
        name: 'vin.jpg',
      });
      const res = await fetch(`${API_URL}/scan-vin-image`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (data.vin) setVin(data.vin);
    }
  };

  return (
    <ScrollView contentContainerStyle={{ padding: 20 }}>
      <TextInput
        placeholder="Enter VIN"
        value={vin}
        onChangeText={setVin}
        style={{ borderWidth: 1, padding: 10, marginVertical: 10 }}
      />
      <Button title="Scan VIN with Camera" onPress={scanVin} />
      <Button title="Decode" onPress={decodeVin} disabled={loading} />
      {result && (
        <View style={{ marginTop: 20 }}>
          <Text>Make: {result.make}</Text>
          <Text>Model: {result.model}</Text>
          <Text>Year: {result.year}</Text>
          <Text>Trim (ML): {result.trim}</Text>
          <Text>Engine (ML): {result.engine}</Text>
        </View>
      )}
    </ScrollView>
  );
}