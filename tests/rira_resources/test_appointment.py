from rnds.rira_resources.appointment import Appointment


def test_appointment_init():
    app = Appointment(
        app_status="booked",
        app_service_category_code="04",
        app_service_type_code="0209010029",
        app_specialty_code="225225",
        app_type_code="routine",
        app_start_time="2023-01-01T10:00:00",
        app_end_time="2023-01-01T11:00:00",
        app_created_time="2023-01-01T09:00:00",
        app_patient_id="123",
        app_participant_type_code="PCT",
        app_participant_status="accepted",
    )
    assert app.app_status == "booked"
    assert app.gerar_dict("1", "2")["status"] == "booked"
