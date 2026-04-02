import { useState, useEffect } from "react";
import { Alert, Form, Button, Row, Col } from "react-bootstrap";

function getQuestionType(question) {
  if (question.question_type === "radio") {
    if (question.options.length === 1 && question.options[0].has_text) return "text";
    return "radio";
  }
  if (question.question_type === "multiple_choice") {
    if (question.options.length === 1 && question.options[0].has_text) return "text";
    return "checkbox";
  }
  return "text";
}

function getQuestionMandatory(question) {
  return question.question_type === "radio";
}

const FormComponent = ({ questions, onSubmit, disabled, initialFormData = {} }) => {
  const [formData, setFormData] = useState(initialFormData);
  const [validated, setValidated] = useState(false);

  // Update formData if initialFormData changes in props
  useEffect(() => {
    setFormData(initialFormData);
  }, [initialFormData]);

  const handleChange = (e, question_id, option_id) => {
    const { type, value, checked } = e.target;
    const currentData = formData[question_id] || { question_id, option_ids: [], option_texts: [] };

    if (type === "checkbox") {
      let newOptionIds = [...currentData.option_ids];
      let newTexts = [...currentData.option_texts];

      if (checked) {
        newOptionIds.push(option_id);
        newTexts.push("");
      } else {
        const index = newOptionIds.indexOf(option_id);
        newOptionIds.splice(index, 1);
        newTexts.splice(index, 1);
      }

      setFormData({
        ...formData,
        [question_id]: { ...currentData, option_ids: newOptionIds, option_texts: newTexts },
      })
    } else if (type === "radio") {
      setFormData({
        ...formData,
        [question_id]: { question_id, option_ids: [option_id], option_texts: [""] },
      });
    } else if (type === "text") {
      setFormData({
        ...formData,
        [question_id]: { question_id, option_ids: [option_id], option_texts: [value] },
      });
    }
  };

  const handleOther = (e, question_id, option_id) => {
    const { value } = e.target;
    const currentData = formData[question_id];
    if (!currentData) return;

    const index = currentData.option_ids.indexOf(option_id);
    if (index === -1) return;

    setFormData({
      ...formData,
      [question_id]: {
        ...currentData,
        option_texts: currentData.option_texts.map((text, i) => (i === index ? value : text)),
      },
    });
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    if (form.checkValidity() === false) {
      event.stopPropagation();
    } else {
      onSubmit({ ...formData });
    }
    setValidated(true);
  };

  const linkify = (text) => {
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    return text.split(urlRegex).map((part, index) => {
      if (part.match(urlRegex)) {
        const displayText = part.replace(/^https?:\/\//, "");
        return (
          <a key={index} href={part} target="_blank" rel="noopener noreferrer">
            {displayText}
          </a>
        );
      }
      return part;
    });
  };

  const isOptionSelected = (question_id, option_id) => {
    const data = formData[question_id];
    return data ? data.option_ids.includes(option_id) : false;
  };

  const getOptionText = (question_id, option_id) => {
    const data = formData[question_id];
    if (!data) return "";
    const index = data.option_ids.indexOf(option_id);
    return index !== -1 ? data.option_texts[index] : "";
  };

  const renderForm = () => (
    <Form noValidate validated={validated} onSubmit={handleSubmit}>
    <fieldset disabled={disabled}>
      {questions.map((question) => (
        <Form.Group key={question.id} className="mb-3">
          <Form.Label>{question.title}</Form.Label>
          <Form.Text className="text-muted">
            {getQuestionMandatory(question) && <span className="text-danger"> *</span>}
          </Form.Text>
          <div>
            <Form.Text className="text-muted">{linkify(question.description)}</Form.Text>
          </div>
          {getQuestionType(question) === "text" && (
            <Form.Control
              type="text"
              required={getQuestionMandatory(question)}
              value={getOptionText(question.id, question.options[0].id)}
              onChange={(e) => handleChange(e, question.id, question.options[0].id)}
            />
          )}
          {getQuestionType(question) !== "text" && (
            <>
              {question.options.map((option, index) => (
                <div key={index}>
                  {option.has_text === false && (
                    <Form.Check
                      type={getQuestionType(question)}
                      name={`question.${question.id}`}
                      label={`${option.name}${option.price > 0 ? ` (+${option.price}kr)` : ""}`}
                      required={getQuestionMandatory(question)}
                      checked={isOptionSelected(question.id, option.id)}
                      onChange={(e) => handleChange(e, question.id, option.id)}
                    />
                  )}
                  {option.has_text !== false && (
                    <Row className="align-items-center justify-content-start" style={{ padding: 0 }}>
                      <Col xs="auto">
                        <Form.Check
                          type={getQuestionType(question)}
                          name={`question.${question.id}`}
                          label={`${option.name}${option.price > 0 ? ` (+${option.price}kr)` : ""}`}
                          required={getQuestionMandatory(question)}
                          checked={isOptionSelected(question.id, option.id)}
                          onChange={(e) => handleChange(e, question.id, option.id)}
                        />
                      </Col>
                      <Col xs="auto">
                        <Form.Control
                          type="text"
                          value={getOptionText(question.id, option.id)}
                          onChange={(e) => handleOther(e, question.id, option.id)}
                          required={isOptionSelected(question.id, option.id)}
                        />
                      </Col>
                    </Row>
                  )}
                </div>
              ))}
            </>
          )}
        </Form.Group>
      ))}

      <Button type="submit">Anmäl</Button>
    </fieldset> 
    </Form>
    
  );

  return renderForm();
};

export default FormComponent;

