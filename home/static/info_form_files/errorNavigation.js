(function(global, factory) {
  typeof exports === "object" && typeof module !== "undefined"
    ? (module.exports = factory())
    : typeof define === "function" && define.amd
      ? define(factory)
      : ((global = global || self), (global.ErrorNavigation = factory()));
})(this, function() { 'use strict';
  var state = {
    section: null,
    current: -1,
    errors: [],
  };

  function getMessage() {
    if (state.errors.length <= 0) {
      return 'Well done! All errors are fixed.';
    }
    if (state.errors.length === 1) {
      return 'There is <strong>an error</strong> in this page. Please correct it before move on.';
    }

    var msg = 'There are <strong>{count} errors</strong> in this page. Please correct them before move on.';
    msg = msg.replace('{count}', state.errors.length);
    return msg;
  }

  function createNavigation(section) {
    var container = document.createElement('div');
    container.classList.add('error-navigation-container');
    container.style.display = 'none';
    container.setAttribute('aria-hidden', 'true');

    var inner = document.createElement('div');
    inner.classList.add('error-navigation-inner');
    container.appendChild(inner);

    var message = document.createElement('span');
    message.classList.add('error-navigation-message');
    inner.appendChild(message);

    var nextButton = document.createElement('button');
    nextButton.classList.add('error-navigation-next-button');
    nextButton.type = 'button';
    nextButton.innerText = 'See Errors';
    nextButton.addEventListener('click', focusToNextError);
    inner.appendChild(nextButton);

    var doneButton = document.createElement('button');
    doneButton.classList.add('error-navigation-done-button');
    doneButton.type = 'button';
    doneButton.innerText = 'Done';
    doneButton.style.display = 'none';
    doneButton.addEventListener('click', close);
    inner.appendChild(doneButton);

    section.appendChild(container);
    return container;
  }

  function destroyNavigation(section) {
    var nav = section.querySelector('.error-navigation-container');
    if (nav) {
      nav.remove();
    }
  }

  function focusToNextError() {
    var nextCurrent = (state.current + 1) % state.errors.length;
    var erroredLine = state.errors[nextCurrent];
    if (!erroredLine) {
      return;
    }
    var erroredField = erroredLine.querySelector('.form-validation-error');
    if (!erroredField) {
      return;
    }
    state.current = nextCurrent;
    erroredLine.scrollIntoView({ behavior: 'smooth', block: 'center' });
    erroredField.focus({ preventScroll: true });
  }

  function close() {
    window.scrollTo({ left: 0, top: document.body.scrollHeight, behavior: 'smooth' });

    var bottomInterval = setInterval(function() {
      if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight) {
        clearInterval(bottomInterval);
        var errCont = state.section.querySelector('.error-navigation-container');
        if (errCont) {
            errCont.classList.add('fading-out');
        }
        setTimeout(function(){
          destroyNavigation(state.section);
        }, 210);
      }
    }, 100);
  }

  return {
    update: function update(section, render) {
      if (!section) {
        var sections = document.querySelectorAll('.form-section.page-section');
        if (sections.length <= 0) {
          return;
        }
        section = sections[(sections.length - 1)];
      }
      state.section = section;

      var invalidFields = state.section.querySelectorAll('.form-line.form-line-error');

      if (invalidFields.length <= 0 && state.errors.length <= 0) {
        destroyNavigation(state.section);
        return;
      }

      state.errors = invalidFields;

      var nav = state.section.querySelector('.error-navigation-container');
      if (!nav) {
        if (!render) {
          return;
        }
        nav = createNavigation(state.section);
      }

      if (state.errors.length > 0) {
        nav.querySelector('.error-navigation-next-button').style.display = 'block';
        nav.querySelector('.error-navigation-done-button').style.display = 'none';
        nav.classList.remove('is-success');
      } else {
        nav.classList.add('is-success');
        nav.querySelector('.error-navigation-next-button').style.display = 'none';
        nav.querySelector('.error-navigation-done-button').style.display = 'block';
      }

      nav.querySelector('.error-navigation-message').innerHTML = getMessage();

      // show navigation
      nav.style.display = null;
      nav.classList.remove('fading-out');
    },
  };
});
