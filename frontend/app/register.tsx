import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuthStore } from '../src/store/authStore';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';

const API_URL = 'https://absence-alert-4.preview.emergentagent.com';

export default function Register() {
  const router = useRouter();
  const { register, loading } = useAuthStore();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    phone: '',
    role: 'teacher' as 'platform_admin' | 'school_admin' | 'teacher' | 'parent',
    school_cnn: '',
    student_roll: '',
    otp_code: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [otpSent, setOtpSent] = useState(false);
  const [otpData, setOtpData] = useState<any>(null);

  const roles = [
    { value: 'teacher', label: 'Teacher', icon: 'person' },
    { value: 'school_admin', label: 'School Admin', icon: 'business' },
    { value: 'parent', label: 'Parent', icon: 'people' },
  ];

  const handleRequestOTP = async () => {
    if (!formData.school_cnn || !formData.student_roll) {
      Alert.alert('Error', 'Please enter school CNN token and student roll number');
      return;
    }

    try {
      const response = await axios.post(`${API_URL}/api/parent/request-otp`, {
        school_cnn: formData.school_cnn,
        roll_number: formData.student_roll,
      });
      setOtpData(response.data);
      setOtpSent(true);
      Alert.alert(
        'OTP Sent',
        `OTP has been sent to phone ending in ${response.data.phone}\n\n[Dev] OTP: ${response.data.otp}`
      );
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to send OTP');
    }
  };

  const handleRegister = async () => {
    if (!formData.email || !formData.password || !formData.name) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    if (formData.role === 'parent' && !otpSent) {
      Alert.alert('Error', 'Please request and verify OTP first');
      return;
    }

    try {
      await register(formData);
      
      // Load school branding if CNN token was used
      if (formData.school_cnn) {
        const { loadBranding } = await import('../src/store/brandingStore');
        const store = await import('../src/store/brandingStore');
        await store.useBrandingStore.getState().loadBranding(formData.school_cnn);
      }
      
      router.replace('/');
    } catch (error: any) {
      Alert.alert('Registration Failed', error.message);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => router.back()}
          >
            <Ionicons name="arrow-back" size={24} color="#6366f1" />
          </TouchableOpacity>
          <Text style={styles.title}>Create Account</Text>
          <Text style={styles.subtitle}>Join AttendSys</Text>
        </View>

        <View style={styles.form}>
          {/* Role Selection */}
          <Text style={styles.label}>Select Role</Text>
          <View style={styles.roleContainer}>
            {roles.map((role) => (
              <TouchableOpacity
                key={role.value}
                style={[
                  styles.roleButton,
                  formData.role === role.value && styles.roleButtonActive,
                ]}
                onPress={() => setFormData({ ...formData, role: role.value as any })}
              >
                <Ionicons
                  name={role.icon as any}
                  size={24}
                  color={formData.role === role.value ? '#6366f1' : '#64748b'}
                />
                <Text
                  style={[
                    styles.roleText,
                    formData.role === role.value && styles.roleTextActive,
                  ]}
                >
                  {role.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          {/* Common Fields */}
          <View style={styles.inputContainer}>
            <Ionicons name="person-outline" size={20} color="#64748b" style={styles.inputIcon} />
            <TextInput
              style={styles.input}
              placeholder="Full Name"
              value={formData.name}
              onChangeText={(text) => setFormData({ ...formData, name: text })}
            />
          </View>

          <View style={styles.inputContainer}>
            <Ionicons name="mail-outline" size={20} color="#64748b" style={styles.inputIcon} />
            <TextInput
              style={styles.input}
              placeholder="Email"
              value={formData.email}
              onChangeText={(text) => setFormData({ ...formData, email: text })}
              autoCapitalize="none"
              keyboardType="email-address"
            />
          </View>

          <View style={styles.inputContainer}>
            <Ionicons name="call-outline" size={20} color="#64748b" style={styles.inputIcon} />
            <TextInput
              style={styles.input}
              placeholder="Phone Number"
              value={formData.phone}
              onChangeText={(text) => setFormData({ ...formData, phone: text })}
              keyboardType="phone-pad"
            />
          </View>

          <View style={styles.inputContainer}>
            <Ionicons name="lock-closed-outline" size={20} color="#64748b" style={styles.inputIcon} />
            <TextInput
              style={styles.input}
              placeholder="Password"
              value={formData.password}
              onChangeText={(text) => setFormData({ ...formData, password: text })}
              secureTextEntry={!showPassword}
            />
            <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
              <Ionicons
                name={showPassword ? 'eye-outline' : 'eye-off-outline'}
                size={20}
                color="#64748b"
              />
            </TouchableOpacity>
          </View>

          {/* School Admin / Teacher - CNN Token */}
          {(formData.role === 'school_admin' || formData.role === 'teacher') && (
            <View style={styles.inputContainer}>
              <Ionicons name="key-outline" size={20} color="#64748b" style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                placeholder="School CNN Token (Optional)"
                value={formData.school_cnn}
                onChangeText={(text) => setFormData({ ...formData, school_cnn: text })}
                autoCapitalize="characters"
              />
            </View>
          )}

          {/* Parent - School CNN + Student Roll & OTP */}
          {formData.role === 'parent' && (
            <>
              <View style={styles.inputContainer}>
                <Ionicons name="key-outline" size={20} color="#64748b" style={styles.inputIcon} />
                <TextInput
                  style={styles.input}
                  placeholder="School CNN Token"
                  value={formData.school_cnn}
                  onChangeText={(text) => setFormData({ ...formData, school_cnn: text })}
                  autoCapitalize="characters"
                />
              </View>

              <View style={styles.inputContainer}>
                <Ionicons name="ribbon-outline" size={20} color="#64748b" style={styles.inputIcon} />
                <TextInput
                  style={styles.input}
                  placeholder="Student Roll Number"
                  value={formData.student_roll}
                  onChangeText={(text) => setFormData({ ...formData, student_roll: text })}
                />
                <TouchableOpacity
                  style={styles.otpButton}
                  onPress={handleRequestOTP}
                >
                  <Text style={styles.otpButtonText}>{otpSent ? 'Resend' : 'Get OTP'}</Text>
                </TouchableOpacity>
              </View>

              {otpSent && (
                <View style={styles.inputContainer}>
                  <Ionicons name="shield-checkmark-outline" size={20} color="#64748b" style={styles.inputIcon} />
                  <TextInput
                    style={styles.input}
                    placeholder="Enter OTP"
                    value={formData.otp_code}
                    onChangeText={(text) => setFormData({ ...formData, otp_code: text })}
                    keyboardType="number-pad"
                    maxLength={6}
                  />
                </View>
              )}
            </>
          )}

          <TouchableOpacity
            style={[styles.button, loading && styles.buttonDisabled]}
            onPress={handleRegister}
            disabled={loading}
          >
            <Text style={styles.buttonText}>{loading ? 'Creating Account...' : 'Register'}</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.linkButton}
            onPress={() => router.back()}
          >
            <Text style={styles.linkText}>Already have an account? Login</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  scrollContent: {
    flexGrow: 1,
    padding: 24,
    paddingTop: 60,
  },
  header: {
    marginBottom: 32,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1e293b',
  },
  subtitle: {
    fontSize: 16,
    color: '#64748b',
    marginTop: 4,
  },
  form: {
    width: '100%',
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 12,
  },
  roleContainer: {
    flexDirection: 'row',
    marginBottom: 24,
    gap: 8,
  },
  roleButton: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 12,
    paddingVertical: 16,
    paddingHorizontal: 8,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#e2e8f0',
  },
  roleButtonActive: {
    borderColor: '#6366f1',
    backgroundColor: '#eef2ff',
  },
  roleText: {
    fontSize: 12,
    color: '#64748b',
    marginTop: 4,
    fontWeight: '500',
  },
  roleTextActive: {
    color: '#6366f1',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  inputIcon: {
    marginRight: 12,
  },
  input: {
    flex: 1,
    fontSize: 16,
    color: '#1e293b',
  },
  otpButton: {
    backgroundColor: '#6366f1',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  otpButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  button: {
    backgroundColor: '#6366f1',
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    marginTop: 8,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  linkButton: {
    marginTop: 24,
    alignItems: 'center',
  },
  linkText: {
    color: '#6366f1',
    fontSize: 14,
  },
});
