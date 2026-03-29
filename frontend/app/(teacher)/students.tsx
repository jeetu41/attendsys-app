import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  Modal,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import { getAuthHeader } from '../../src/store/authStore';

const API_URL = 'https://absence-alert-4.preview.emergentagent.com';

interface Student {
  _id: string;
  name: string;
  roll_number: string;
  class_name: string;
  parent_phone: string;
  parent_email?: string;
  student_token: string;
  attendance_percentage: number;
  total_days: number;
}

export default function StudentsScreen() {
  const [students, setStudents] = useState<Student[]>([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    roll_number: '',
    class_name: '',
    parent_phone: '',
    parent_email: '',
  });
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);

  useEffect(() => {
    loadStudents();
  }, []);

  const loadStudents = async () => {
    try {
      const headers = await getAuthHeader();
      const response = await axios.get(`${API_URL}/api/teacher/students`, { headers });
      setStudents(response.data);
    } catch (error) {
      console.error('Failed to load students:', error);
      Alert.alert('Error', 'Failed to load students');
    }
  };

  const addStudent = async () => {
    if (!formData.name || !formData.roll_number || !formData.class_name || !formData.parent_phone) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      const headers = await getAuthHeader();
      await axios.post(`${API_URL}/api/teacher/students`, formData, { headers });
      Alert.alert('Success', 'Student added successfully');
      setShowAddModal(false);
      setFormData({
        name: '',
        roll_number: '',
        class_name: '',
        parent_phone: '',
        parent_email: '',
      });
      await loadStudents();
    } catch (error: any) {
      console.error('Failed to add student:', error);
      Alert.alert('Error', error.response?.data?.detail || 'Failed to add student');
    } finally {
      setLoading(false);
    }
  };

  const showStudentToken = (student: Student) => {
    Alert.alert(
      'Student Token',
      `Share this token with the parent for registration:\n\n${student.student_token}`,
      [
        { text: 'Close', style: 'cancel' },
      ]
    );
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadStudents();
    setRefreshing(false);
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>My Students ({students.length})</Text>
        <TouchableOpacity
          style={styles.addButton}
          onPress={() => setShowAddModal(true)}
        >
          <Ionicons name="add" size={24} color="#fff" />
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {students.length === 0 ? (
          <View style={styles.emptyState}>
            <Ionicons name="people-outline" size={64} color="#cbd5e1" />
            <Text style={styles.emptyText}>No students yet</Text>
            <Text style={styles.emptySubtext}>Tap + to add your first student</Text>
          </View>
        ) : (
          students.map((student) => (
            <TouchableOpacity
              key={student._id}
              style={styles.studentCard}
              onPress={() => setSelectedStudent(student)}
            >
              <View style={styles.studentHeader}>
                <View style={styles.studentIcon}>
                  <Ionicons name="person" size={24} color="#6366f1" />
                </View>
                <View style={styles.studentInfo}>
                  <Text style={styles.studentName}>{student.name}</Text>
                  <Text style={styles.studentDetails}>
                    Roll: {student.roll_number} • Class: {student.class_name}
                  </Text>
                </View>
              </View>

              <View style={styles.studentStats}>
                <View style={styles.stat}>
                  <Text style={styles.statLabel}>Attendance</Text>
                  <Text style={styles.statValue}>{student.attendance_percentage}%</Text>
                </View>
                <View style={styles.stat}>
                  <Text style={styles.statLabel}>Total Days</Text>
                  <Text style={styles.statValue}>{student.total_days}</Text>
                </View>
              </View>

              <TouchableOpacity
                style={styles.tokenButton}
                onPress={(e) => {
                  e.stopPropagation();
                  showStudentToken(student);
                }}
              >
                <Ionicons name="key" size={16} color="#6366f1" />
                <Text style={styles.tokenButtonText}>View Token</Text>
              </TouchableOpacity>
            </TouchableOpacity>
          ))
        )}
      </ScrollView>

      {/* Add Student Modal */}
      <Modal
        visible={showAddModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowAddModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Add Student</Text>
              <TouchableOpacity onPress={() => setShowAddModal(false)}>
                <Ionicons name="close" size={24} color="#64748b" />
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.form}>
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Student Name *</Text>
                <TextInput
                  style={styles.input}
                  placeholder="Enter full name"
                  value={formData.name}
                  onChangeText={(text) => setFormData({ ...formData, name: text })}
                />
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Roll Number *</Text>
                <TextInput
                  style={styles.input}
                  placeholder="Enter roll number"
                  value={formData.roll_number}
                  onChangeText={(text) => setFormData({ ...formData, roll_number: text })}
                />
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Class *</Text>
                <TextInput
                  style={styles.input}
                  placeholder="e.g., 5A, 10B"
                  value={formData.class_name}
                  onChangeText={(text) => setFormData({ ...formData, class_name: text })}
                />
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Parent Phone *</Text>
                <TextInput
                  style={styles.input}
                  placeholder="Enter phone number"
                  value={formData.parent_phone}
                  onChangeText={(text) => setFormData({ ...formData, parent_phone: text })}
                  keyboardType="phone-pad"
                />
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Parent Email (Optional)</Text>
                <TextInput
                  style={styles.input}
                  placeholder="Enter email address"
                  value={formData.parent_email}
                  onChangeText={(text) => setFormData({ ...formData, parent_email: text })}
                  keyboardType="email-address"
                  autoCapitalize="none"
                />
              </View>
            </ScrollView>

            <TouchableOpacity
              style={[styles.submitButton, loading && styles.submitButtonDisabled]}
              onPress={addStudent}
              disabled={loading}
            >
              <Text style={styles.submitButtonText}>
                {loading ? 'Adding...' : 'Add Student'}
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>

      {/* Student Details Modal */}
      <Modal
        visible={!!selectedStudent}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setSelectedStudent(null)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            {selectedStudent && (
              <>
                <View style={styles.modalHeader}>
                  <Text style={styles.modalTitle}>Student Details</Text>
                  <TouchableOpacity onPress={() => setSelectedStudent(null)}>
                    <Ionicons name="close" size={24} color="#64748b" />
                  </TouchableOpacity>
                </View>

                <ScrollView style={styles.detailsContent}>
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Name</Text>
                    <Text style={styles.detailValue}>{selectedStudent.name}</Text>
                  </View>

                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Roll Number</Text>
                    <Text style={styles.detailValue}>{selectedStudent.roll_number}</Text>
                  </View>

                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Class</Text>
                    <Text style={styles.detailValue}>{selectedStudent.class_name}</Text>
                  </View>

                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Parent Phone</Text>
                    <Text style={styles.detailValue}>{selectedStudent.parent_phone}</Text>
                  </View>

                  {selectedStudent.parent_email && (
                    <View style={styles.detailRow}>
                      <Text style={styles.detailLabel}>Parent Email</Text>
                      <Text style={styles.detailValue}>{selectedStudent.parent_email}</Text>
                    </View>
                  )}

                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Student Token</Text>
                    <Text style={styles.detailValue}>{selectedStudent.student_token}</Text>
                  </View>

                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Attendance</Text>
                    <Text style={styles.detailValue}>
                      {selectedStudent.attendance_percentage}% ({selectedStudent.total_days} days)
                    </Text>
                  </View>
                </ScrollView>
              </>
            )}
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e2e8f0',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1e293b',
  },
  addButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#6366f1',
    alignItems: 'center',
    justifyContent: 'center',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 64,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#64748b',
    marginTop: 16,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#94a3b8',
    marginTop: 8,
  },
  studentCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  studentHeader: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  studentIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#eef2ff',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  studentInfo: {
    flex: 1,
  },
  studentName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1e293b',
  },
  studentDetails: {
    fontSize: 14,
    color: '#64748b',
    marginTop: 4,
  },
  studentStats: {
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: '#f1f5f9',
    paddingTop: 12,
    marginBottom: 12,
  },
  stat: {
    flex: 1,
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 12,
    color: '#64748b',
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1e293b',
    marginTop: 4,
  },
  tokenButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#eef2ff',
    paddingVertical: 10,
    borderRadius: 8,
    gap: 6,
  },
  tokenButtonText: {
    color: '#6366f1',
    fontSize: 14,
    fontWeight: '600',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingTop: 24,
    paddingHorizontal: 24,
    paddingBottom: 40,
    maxHeight: '90%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1e293b',
  },
  form: {
    marginBottom: 24,
  },
  inputGroup: {
    marginBottom: 16,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#f8fafc',
    borderWidth: 1,
    borderColor: '#e2e8f0',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    color: '#1e293b',
  },
  submitButton: {
    backgroundColor: '#6366f1',
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
  },
  submitButtonDisabled: {
    opacity: 0.6,
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  detailsContent: {
    marginBottom: 24,
  },
  detailRow: {
    marginBottom: 16,
  },
  detailLabel: {
    fontSize: 12,
    color: '#64748b',
    marginBottom: 4,
  },
  detailValue: {
    fontSize: 16,
    color: '#1e293b',
    fontWeight: '500',
  },
});
